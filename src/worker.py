#!/usr/bin/env python3.6

import json
import logging.config
import os
import threading

from vlibras_translate import translation

from utils import configreader
from utils import queuewrapper


class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__translator = self.__get_translator()
        self.__consumer = queuewrapper.QueueConsumer()
        self.__publisher = queuewrapper.QueuePublisher()

    def __get_translator(self):
        try:
            self.__logger.debug("Instantiating vlibras_translate.")
            return translation.Translation()
        except vlibras_translate.exceptions.LemmaException as ex:
            raise ex

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new translation request.")
            payload = json.loads(body)
            gloss = self.__translator.rule_translation(payload.get("text", ""))

            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"translation": gloss}),
                id=properties.correlation_id)

        except json.JSONDecodeError:
            self.__logger.exception("Received an invalid translation request.")
            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": "Body is not a valid JSON"}),
                id=properties.correlation_id)

        except vlibras_translate.exceptions.LemmaException:
            self.__logger.exception(
                "vlibras_translate failed to translate text.")
            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": "Failed to translate text."}),
                id=properties.correlation_id)

            del self.__translator
            self.__translator = self.__get_translator()

        except Exception:
            self.__logger.exception("An unexpected exception occurred.")
            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": "Translator internal error."}),
                id=properties.correlation_id)

        finally:
            if channel.is_open:
                channel.basic_ack(delivery_tag=method.delivery_tag)

    def __reply_message(self, route, message, id):
        self.__logger.info("Sending response to request.")

        if id is None:
            self.__logger.error("The request don't have correlation_id.")

        if route is None:
            self.__logger.error("The request don't have reply_to route.")
        else:
            self.__publisher.publish_to_queue(route, message, id)

    def start(self, queue):
        self.__logger.debug("Starting queue consumer.")
        self.__consumer.consume_from_queue(queue, self.__process_message)

    def stop(self):
        self.__logger.debug("Stopping queue consumer.")
        self.__consumer.close_connection()
        self.__logger.debug("Stopping queue publisher.")
        self.__publisher.close_connection()


if __name__ == "__main__":
    logging.config.fileConfig(os.environ.get("LOGGER_CONFIG_FILE", ""))
    logger = logging.getLogger(__name__)

    workercfg = configreader.load_configs("Worker")

    if not workercfg:
        raise SystemExit(1)

    try:
        logger.info("Creating Translation Worker.")
        worker = Worker()
        logger.info("Starting Translation Worker.")
        worker.start(workercfg.get("TranslatorQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping Translation Worker.")

    except Exception:
        logger.exception("Unexpected error has occured in Translation Worker.")

    finally:
        worker.stop()
        raise SystemExit(1)
