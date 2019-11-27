import logging

from json import JSONDecodeError
from unity import playerwrapper
from pymodm import errors as ODMError
from pymongo import errors as MongoError


def handle_exception(ex):
    logger = logging.getLogger(__name__)

    try:
        if isinstance(ex, JSONDecodeError):
            logger.exception("Received an invalid video generation request.")
        elif isinstance(ex, playerwrapper.RenderingError):
            logger.exception("Libras video not generated.")
        elif isinstance(ex, MongoError.ServerSelectionTimeoutError):
            logger.exception("Worker not connected to database.")
        elif isinstance(ex, ODMError.DoesNotExist):
            logger.exception("Failed to get request data.")
        else:
            logger.exception("An unexpected exception occurred.")

    except TypeError:
        logger.exception("An error occurred while handling an exception.")
