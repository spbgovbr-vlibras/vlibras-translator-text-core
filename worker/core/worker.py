#!/usr/bin/env python3

import json
import logging.config
import os
import threading

from db import attributes
from db import videodb
from player import playerwrapper
from utils import configreader
from utils import queuewrapper

class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__database = videodb.VideoDB()
        self.__consumer = queuewrapper.QueueConsumer()
        self.__videomaker = playerwrapper.PlayerWrapper()

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new video generation request.")
            payload = json.loads(body)

            self.__database.update_video_document(
                video_uid=properties.correlation_id,
                video_status=attributes.VideoStatus.PROCESSING.name)

            path, size, duration = self.__videomaker.run(
                payload.get("gloss", ""),
                properties.correlation_id,
                payload.get("options", {}))

            self.__database.update_video_document(
                video_uid=properties.correlation_id,
                video_status=attributes.VideoStatus.GENERATED.name,
                video_path=path,
                video_size=size,
                video_duration=duration)

        except json.JSONDecodeError:
            self.__logger.exception("Received an invalid video generation request.")
            self.__database.update_video_document(
                video_uid=properties.correlation_id,
                video_status=attributes.VideoStatus.FAILED.name)

        except Exception:
            self.__logger.exception("An unexpected exception occurred.")
            self.__database.update_video_document(
                video_uid=properties.correlation_id,
                video_status=attributes.VideoStatus.FAILED.name)

    def start(self, queue):
        self.__logger.debug("Connecting to database.")
        self.__database.connect()
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

    try:
        worker = Worker()
        logger.info("Starting VideoMaker Worker.")
        worker.start(workercfg.get("VideomakerQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping VideoMaker Worker.")

    except Exception:
        logger.exception("Failed to start VideoMaker Worker.")

    finally:
        worker.stop()
        raise SystemExit(0)
