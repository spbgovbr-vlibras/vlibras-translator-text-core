#!/usr/bin/env python3

import json
import logging.config
import os
import threading

from player import playerwrapper
from utils import configreader
from utils import healthserver
from utils import queuewrapper

class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__consumer = queuewrapper.QueueConsumer()
        self.__videomaker = playerwrapper.PlayerWrapper()

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new video generation request.")
            payload = json.loads(body)

            video = self.__videomaker.run(
                payload.get("text", ""), 
                properties.correlation_id)

            # Update DB here

        except json.JSONDecodeError:
            self.__logger.exception("Received an invalid video generation request.")
            # Update DB here

        except Exception:
            self.__logger.exception("An unexpected exception occurred.")

    def start(self, queue):
        self.__logger.debug("Starting queue consumer.")
        self.__consumer.consume_from_queue(queue, self.__process_message)

    def stop(self):
        self.__logger.debug("Stopping queue consumer.")
        self.__consumer.close_connection()

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

        logger.info("VideoMaker Worker Started.")
        worker.start(workercfg.get("VideomakerQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping VideoMaker Worker.")

    except Exception:
        logger.exception("Failed to start VideoMaker Worker.")

    finally:
        worker.stop()
        raise SystemExit(0)
