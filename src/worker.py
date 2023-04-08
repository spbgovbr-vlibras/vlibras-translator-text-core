#!/usr/bin/env python3.6

import json
import logging.config
import os

from vlibras_translate import translation
# from util import RabbitRefreshConnection

from util import configreader
from util import exceptionhandler
from util import healthcheck
from util import queuewrapper
from util import rabbitconnectionrefresh


class Worker:

    def __init__(self, dlmode):
        self.__logger = logging.getLogger(self.__class__.__name__)

        if (dlmode == "true"):
            self.__translate = translation.Translation().rule_translation_with_dl
        else:
            self.__translate = translation.Translation().rule_translation

        self.consumer = queuewrapper.QueueConsumer()
        self.publisher = queuewrapper.QueuePublisher()

        self.rabbitconnectionrefresh = rabbitconnectionrefresh.RabbitRefreshConnection(self.consumer, self.publisher)
        self.rabbitconnectionrefresh.start() 

    def __reply_message(self, route, message, id):
        self.__logger.info("Sending response to request.")

        if id is None:
            self.__logger.error("The request don't have correlation_id.")

        if route is None:
            self.__logger.error("The request don't have reply_to route.")
        else:
            self.publisher.publish_to_queue(route, message, id)

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new translation request.")
            payload = json.loads(body)
            gloss = self.__translate(payload.get("text", ""))

            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"translation": gloss}),
                id=properties.correlation_id)

        except Exception as ex:
            exceptionhandler.handle_exception(ex)

            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({"error": "Translator internal error."}),
                id=properties.correlation_id)

        finally:
            if channel.is_open:
                channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self, queue):
        self.__logger.debug("Starting queue consumer.")
        self.consumer.consume_from_queue(queue, self.__process_message)

    def stop(self):
        self.__logger.debug("Stopping queue consumer.")
        self.consumer.close_connection()
        self.__logger.debug("Stopping queue publisher.")
        self.publisher.close_connection()


if __name__ == "__main__":
    logging.config.fileConfig(os.environ.get("LOGGER_CONFIG_FILE", ""))
    logger = logging.getLogger(__name__)

    workercfg = configreader.load_configs("Worker")

    if not workercfg:
        raise SystemExit(1)

    try:
        healthcheck.run_healthcheck_thread(workercfg.get("HealthServerPort"))
        logger.info("Creating Translation Worker.")
        worker = Worker(workercfg.get("DLTranslationMode", "false"))
        logger.info("Starting Translation Worker.")
        worker.start(workercfg.get("TranslatorQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping Translation Worker.")

    except Exception:
        logger.exception("Unexpected error has occured in Translation Worker.")

    finally:
        worker.stop()
        raise SystemExit(1)
