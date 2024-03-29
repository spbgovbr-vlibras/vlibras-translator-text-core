#!/usr/bin/env python3.6

import json
import logging.config
import os
import datetime

from database import connection
from database.attributes import VideoStatus
from database.models import Videos
from database.models import StatusVideosTranslations

from player import playerwrapper
from util import configreader
from util import exceptionhandler
from util import healthcheck
from util import queuewrapper


class Worker:

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__consumer = queuewrapper.QueueConsumer()
        self.__videomaker = playerwrapper.PlayerWrapper()

    def __process_message(self, channel, method, properties, body):
        try:
            self.__logger.info("Processing a new video generation request.")
            videoRequest = None
            statusVideosTranslations = None

            payload = json.loads(body)
            videoRequest = Videos.objects.get(
                {"uid": properties.correlation_id})

            videoRequest.status = VideoStatus.GENERATING.name.lower()

            videoRequest.save()

            print('############# GENERATING #############')
            print(VideoStatus.GENERATING.name.lower())
            print(datetime.datetime.utcnow())
            print(datetime.datetime.utcnow())

            StatusVideosTranslations(
                VideoStatus.GENERATING.name.lower(),
                0,
                datetime.datetime.utcnow(),
                datetime.datetime.utcnow(),
            ).save()
            print('############# SAIU GENERATING #############')


            video_path, video_size, video_duration = self.__videomaker.run(
                payload.get("gloss", ""),
                properties.correlation_id,
                payload.get("playerOptions", {}))

            videoRequest.status = VideoStatus.GENERATED.name.lower()
            videoRequest.path = video_path
            videoRequest.size = video_size
            videoRequest.duration = video_duration
            videoRequest.save()

            print('############# GENERATED #############')
            print(VideoStatus.GENERATED.name.lower())
            print(video_duration)
            print(datetime.datetime.utcnow())

            StatusVideosTranslations(
                VideoStatus.GENERATED.name.lower(),
                video_duration,
                datetime.datetime.utcnow(),
                datetime.datetime.utcnow(),
            ).save()
            print('############# SAIU GENERATED #############')

        except Exception as ex:
            exceptionhandler.handle_exception(ex)
            if videoRequest is not None:
                videoRequest.status = VideoStatus.FAILED.name.lower()
                try:
                    videoRequest.save()

                    print('############# FAILED #############')
                    print(VideoStatus.FAILED.name.lower())
                    print(datetime.datetime.utcnow())

                    StatusVideosTranslations(
                        VideoStatus.FAILED.name.lower(),
                        0,
                        datetime.datetime.utcnow(),
                        datetime.datetime.utcnow(),
                    ).save()
                    print('############# SAIU FAILED #############')

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

    if not workercfg:
        raise SystemExit(1)

    try:
        connection.connect_to_database()
        healthcheck.run_healthcheck_thread(workercfg.get("HealthServerPort"))
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
