import json
import logging
import threading

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


class Worker:
    """Main worker"""

    def __init__(self, translator_queue: str, neural: bool = True):
        """Constructor."""
        self.consumer = QueueConsumer()
        self.publisher = QueuePublisher()

        self.translator_queue = translator_queue

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
        """Do worker task"""

        logger.debug("Processing a new request on a separate thread")

        try:
            logger.info("Processing a new translation request.")
            payload = json.loads(body)
            gloss = self.translate(payload.get("text", ""))

            message = json.dumps({
                'translation': gloss,
                'version': self.version
            })

            self.reply_message(
                route=properties.reply_to,
                message=message,
                id=properties.correlation_id
            )

        except Exception as ex:
            handle_exception(ex)

            self.reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": "Translator internal error."}),
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

        # Clean up the list of threads, so it doesn't keep appending
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
        """Start message queue consumer"""
        logger.debug("Starting queue consumer")
        self.consumer.consume_from_queue(
            self.translator_queue,
            self.process_message,
        )

        for thread in self.threads:
            thread.join()

        self.consumer._connection.process_data_events()
        self.consumer.close_connection()

    def exit_gracefully(self, signum, frame):
        """Stop consuming queue but finish current messages."""
        self.consumer.stop_consuming()

    def stop(self):
        """Stop message queue consumers."""
        logger.debug("Stopping queue consumer")
        self.consumer.close_connection()
        logger.debug("Stopping queue publisher")
        self.publisher.close_connection()


if __name__ == "__main__":

    from signal import SIGTERM, signal

    worker = None

    try:
        logger.info("Trying to create translation worker")

        run_healthcheck_thread(settings.HEALTHCHECK_PORT)

        worker = Worker(
            translator_queue=settings.TRANSLATOR_QUEUE,
            neural=settings.ENABLE_DL_TRANSLATION
        )

        logger.info("Starting translation worker")

        signal(SIGTERM, worker.exit_gracefully)
        worker.start()

    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: stopping translation worker")
    except Exception:
        logger.exception("Unexpected error has occured in translation worker")
    finally:
        if worker:
            worker.stop()
            SystemExit(1)
