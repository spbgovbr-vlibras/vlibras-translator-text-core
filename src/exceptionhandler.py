import logging

from json import JSONDecodeError


def handle_exception(ex):
    logger = logging.getLogger(__name__)

    try:
        if isinstance(ex, JSONDecodeError):
            logger.exception("Received an invalid translation request.")
        else:
            logger.exception("An unexpected exception occurred.")

    except TypeError:
        logger.exception("An error occurred while handling an exception.")
