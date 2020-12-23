import logging

from pymodm import connect

from util import configreader


def connect_to_database():
    logger = logging.getLogger(__name__)

    mongocfg = configreader.load_configs("MongoDB")
    mongourl = "mongodb://{}:{}@{}:{}/{}".format(
        mongocfg.get("DBUser", "None"),
        mongocfg.get("DBPass", "None"),
        mongocfg.get("DBHost", "None"),
        mongocfg.get("DBPort", "None"),
        mongocfg.get("DBName", "None"))

    logger.info("Connecting to {}.".format(mongourl))
    connect(mongourl)
