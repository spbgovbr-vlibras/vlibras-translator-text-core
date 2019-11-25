import logging

from pymongo import MongoClient

from db import attributes
from utils import configreader

class VideoDB:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__mongocfg = configreader.load_configs("MongoDB")
        self.__collection = None

    def connect(self):
        self.__logger.debug("Creating MongoDB client connection.")
        mongo_client = MongoClient(
            host=self.__mongocfg.get("DBHost"),
            port=int(self.__mongocfg.get("DBPort")))

        db = self.__mongocfg.get("DBName")
        collection = self.__mongocfg.get("VideoCollection")

        try:
            self.__logger.debug("Getting database '{}'.".format(db))
            self.__logger.debug("Getting collection '{}'.".format(collection))
            self.__collection = mongo_client[db][collection]

        except KeyError:
            self.__logger.error("Failed to access the database.")
            raise

    def update_video_document(
        self,
        video_uid: str,
        video_status: str,
        video_path: str = "",
        video_size: int = 0, 
        video_duration: int = 0
    ) -> None:

        if self.__collection is None:
            self.__logger.error("Attempt to update a document without connection.")
            return

        update_data = { "status": video_status.lower() }

        if video_status == attributes.VideoStatus.GENERATED.name:
            update_data["path"] = video_path
            update_data["size"] = video_size
            update_data["duration"] = video_duration

        self.__logger.debug("Upating document '{}'.".format(video_uid))
        self.__collection.find_one_and_update(
            { "uid": video_uid }, 
            { "$set": update_data })
