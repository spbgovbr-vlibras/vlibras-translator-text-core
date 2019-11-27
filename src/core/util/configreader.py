import configparser
import logging
import os

_CONFIG_FILE = os.environ.get("CORE_CONFIG_FILE", "")
_CONFIG = configparser.SafeConfigParser(os.environ)


def load_configs(section):
    logger = logging.getLogger(__name__)
    logger.debug("Loading {} configs.".format(section))

    try:
        logger.debug("Opening {}.".format(_CONFIG_FILE))
        with open(_CONFIG_FILE) as c_file:
            _CONFIG.read_file(c_file)

    except FileNotFoundError:
        logger.exception("Failed to open {}.".format(_CONFIG_FILE))
        return {}

    if section in _CONFIG:
        logger.debug("Section '{}' loaded successfully.".format(section))
        return _CONFIG[section]

    else:
        logger.error("Failed to load section '{}'.".format(section))
        return {}
