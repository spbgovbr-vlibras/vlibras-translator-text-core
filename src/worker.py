#!/usr/bin/env python3.6

import json
import logging.config
import os

from database import connection
from database.attributes import VideoStatus
from database.models import Videos

from player import playerwrapper
from util import configreader
from util import exceptionhandler
from util import queuewrapper
from util import healthcheck
from threading import Thread

def starting_HC_thread(port):
    hc = healthcheck.healthCheck(port)
    hc.start_HC()


class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__consumer = queuewrapper.QueueConsumer()
        self.__videomaker = playerwrapper.PlayerWrapper()

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new video generation request.")
            videoRequest = None
            payload = json.loads(body)
            videoRequest = Videos.objects.get(
                {"uid": properties.correlation_id})

            videoRequest.status = VideoStatus.GENERATING.name.lower()
            videoRequest.save()

            video_path, video_size, video_duration = self.__videomaker.run(
                payload.get("gloss", ""),
                properties.correlation_id,
                payload.get("playerOptions", {}))

            videoRequest.status = VideoStatus.GENERATED.name.lower()
            videoRequest.path = video_path
            videoRequest.size = video_size
            videoRequest.duration = video_duration
            videoRequest.save()

        except Exception as ex:
            exceptionhandler.handle_exception(ex)
            if videoRequest is not None:
                videoRequest.status = VideoStatus.FAILED.name.lower()
                try:
                    videoRequest.save()
                except Exception as ex:
                    exceptionhandler.handle_exception(ex)

        finally:
            if channel.is_open:
                channel.basic_ack(delivery_tag=method.delivery_tag)

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
    thread = Thread(target = starting_HC_thread, args = (80,))
    thread.start()

    if not workercfg:
        raise SystemExit(1)

    try:
        connection.connect_to_database()
        logger.info("Creating VideoMaker Worker.")
        worker = Worker()
        logger.info("Starting VideoMaker Worker.")
        worker.start(workercfg.get("VideomakerQueue"))

    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: stopping VideoMaker Worker.")

    except Exception:
        logger.exception("Unexpected error has occured in VideoMaker Worker.")

    finally:
        worker.stop()
        raise SystemExit(1)
