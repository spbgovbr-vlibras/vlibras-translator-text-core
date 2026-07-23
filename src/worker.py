import json
import importlib.metadata
import logging
import re
import threading
from collections.abc import Callable
from typing import Any

from vlibras_translator import translate

from config import settings
from exceptionhandler import handle_exception
from healthcheck import run_healthcheck_thread
from queuewrapper import QueueConsumer, QueuePublisher

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseWorker:
    """Base worker for queue consumers."""

    def __init__(
        self,
        worker_name: str,
        queue_name: str,
        handler: Callable[[dict[str, Any]], dict[str, Any]],
    ):
        self.worker_name = worker_name
        self.queue_name = queue_name
        self.handler = handler
        self.consumer = QueueConsumer()
        self.publisher = QueuePublisher()
        self.threads = []

    def ack_message(self, channel, delivery_tag):
        self.consumer._connection.add_callback_threadsafe(
            lambda: channel.basic_ack(delivery_tag),
        )

    def reply_message(self, route, message, id):
        logger.info("Sending response to request.")

        if id is None:
            logger.error("The request don't have correlation_id.")

        if route is None:
            logger.error("The request don't have reply_to route.")
        else:
            self.publisher.publish_to_queue(route, message, id)

    def on_message(self, channel, delivery_tag, properties, body):
        logger.debug("Processing a new request on a separate thread")

        try:
            logger.info("Processing a new %s request.", self.worker_name)
            payload = json.loads(body)
            message = json.dumps(self.handler(payload))

            self.reply_message(
                route=properties.reply_to,
                message=message,
                id=properties.correlation_id
            )

        except Exception as ex:
            handle_exception(ex)

            self.reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": f"{self.worker_name} internal error."}),
                id=properties.correlation_id
            )

        finally:
            if channel.is_open:
                self.ack_message(channel, delivery_tag)

    def process_message(self, channel, method, properties, body):
        """
        The task potentially takes a long time to finish. So, we run
        the task in a separate thread making sure the RabbitMQ I/O
        loop is not blocked.
        """

        for t in self.threads:
            if not t.is_alive():
                t.handled = True
        self.threads = [t for t in self.threads if not t.handled]

        thread = threading.Thread(
            target=self.on_message,
            args=(channel, method.delivery_tag, properties, body),
        )
        thread.handled = False
        thread.start()
        self.threads.append(thread)

    def start(self):
        logger.info("Starting %s consumer on queue '%s'", self.worker_name, self.queue_name)
        self.consumer.consume_from_queue(self.queue_name, self.process_message)

        for thread in self.threads:
            thread.join()

        self.consumer._connection.process_data_events()
        self.consumer.close_connection()

    def exit_gracefully(self, signum, frame):
        self.consumer.stop_consuming()

    def stop(self):
        logger.debug("Stopping %s consumer", self.worker_name)
        self.consumer.close_connection()
        logger.debug("Stopping %s publisher", self.worker_name)
        self.publisher.close_connection()


class TranslationWorker(BaseWorker):
    """Translation worker."""

    def __init__(self, translator_queue: str, neural: bool = True):
        self.translator = translate.Translator()

        self.translate = lambda text: self.translator.translate(
            text,
            neural=neural
        )

        self.version = None

        try:
            self.version = self.translator.version
        # For compatibility with older versions of the vlibras_translator
        except Exception:
            import importlib.metadata
            self.version = importlib.metadata.version("vlibras_translator")
        finally:
            logger.info(
                f'VLibras translator core uses vlibras_translator v{self.version}')

        super().__init__(
            worker_name="translation",
            queue_name=translator_queue,
            handler=self.handle_payload,
        )

    def handle_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        gloss = self.translate(payload.get("text", ""))
        return {
            "translation": gloss,
            "version": self.version,
        }


class GlossRefinementWorker(BaseWorker):
    """Worker backed by vlibras-refiner."""

    DIRECTIONAL_VERB_PATTERN = re.compile(r"\b[1-3][SP]_[^\s]+_[1-3][SP]\b")
    DISAMBIGUATED_VERB_PATTERN = re.compile(r"\b[^\s]+&[^\s]+\b")

    def __init__(self, refinement_queue: str):
        from vlibras_refiner import LLMConfig, Refiner

        self.translator = translate.Translator()
        self.translate = lambda text: self.translator.translate(
            text,
            neural=settings.ENABLE_DL_TRANSLATION,
        )
        self.version = self._resolve_refiner_version()
        self.refiner = Refiner(
            llm_config=LLMConfig(
                provider=settings.LLM_PROVIDER,
                openai_api_key=settings.LLM_API_KEY,
                openai_model=settings.LLM_MODEL,
                openai_base_url=settings.LLM_BASE_URL,
            ),
            verbose=settings.REFINER_VERBOSE,
        )
        super().__init__(
            worker_name="gloss refinement",
            queue_name=refinement_queue,
            handler=self.handle_payload,
        )

    def _resolve_refiner_version(self) -> str:
        try:
            return importlib.metadata.version("vlibras-refiner")
        except importlib.metadata.PackageNotFoundError:
            return "0.2.3b2"

    def handle_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = payload.get("text", "")
        gloss = payload.get("gloss")
        if not text:
            raise ValueError("Gloss refinement payload requires a non-empty 'text' field.")

        if not gloss:
            gloss = self.translate(text)

        if not self._should_refine_gloss(gloss):
            return {
                "translation": gloss,
                "version": self.version,
            }

        result = self.refiner.refine(text, gloss=gloss)
        translation = self._normalize_translation(result)

        return {
            "translation": translation,
            "version": self.version,
        }

    def _should_refine_gloss(self, gloss: str) -> bool:
        return bool(
            self.DIRECTIONAL_VERB_PATTERN.search(gloss)
            or self.DISAMBIGUATED_VERB_PATTERN.search(gloss)
        )

    def _normalize_translation(self, result: Any) -> str:
        if isinstance(result, str):
            return result

        if isinstance(result, dict):
            for key in ("translation", "refined_translation", "gloss", "result"):
                value = result.get(key)
                if isinstance(value, str):
                    return value

        return str(result)


if __name__ == "__main__":

    from signal import SIGTERM, signal

    workers = []
    worker_threads = []

    try:
        logger.info("Trying to create workers")

        run_healthcheck_thread(settings.HEALTHCHECK_PORT)

        workers.append(
            TranslationWorker(
                translator_queue=settings.TRANSLATOR_QUEUE,
                neural=settings.ENABLE_DL_TRANSLATION
            )
        )

        if settings.ENABLE_REFINEMENT:
            workers.append(
                GlossRefinementWorker(
                    refinement_queue=settings.REFINEMENT_QUEUE,
                )
            )
            logger.info(
                "Agent gloss refinement worker enabled with provider '%s'",
                settings.LLM_PROVIDER,
            )
        else:
            logger.info("Agent gloss refinement worker disabled")

        def stop_workers(signum, frame):
            for active_worker in workers:
                active_worker.exit_gracefully(signum, frame)

        logger.info("Starting workers")

        signal(SIGTERM, stop_workers)

        for worker in workers:
            thread = threading.Thread(target=worker.start)
            thread.start()
            worker_threads.append(thread)

        for thread in worker_threads:
            thread.join()

    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: stopping workers")
    except Exception:
        logger.exception("Unexpected error has occured in worker bootstrap")
    finally:
        for worker in workers:
            worker.stop()
