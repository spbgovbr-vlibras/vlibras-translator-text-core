#!/usr/bin/env python3

import json
import logging.config
import os
import threading

from vlibras_translate import translation

from utils import configreader
from utils import healthserver
from utils import queuewrapper

class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__translator = translation.Translation()
        self.__consumer = queuewrapper.QueueConsumer()
        self.__publisher = queuewrapper.QueuePublisher()

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new translation request.")
            payload = json.loads(body)
            gloss = self.__translator.rule_translation(payload.get("text", ""))

            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({ "translation": gloss }),
                id=properties.correlation_id)

        except json.JSONDecodeError:
            self.__logger.exception("Received an invalid translation request.")
            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({ "error": "Body is not a valid JSON" }),
                id=properties.correlation_id)

        except Exception:
            self.__logger.exception("An unexpected exception occurred.")

    def __reply_message(self, route, message, id):
        self.__logger.info("Sending response to request.")

        if id is None:
            self.__logger.warning("The request don't have correlation_id.")

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

    worker = Worker()

    try:
        health_check = threading.Thread(
            target=healthserver.start_server,
            daemon=True)
        health_check.start()

        logger.info("Translation Worker Started.")
        worker.start(workercfg.get("TranslatorQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping Translation Worker.")

    except Exception:
        logger.exception("Failed to start Translation Worker.")

    finally:
        worker.stop()
        raise SystemExit(0)
