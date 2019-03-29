import configparser
import os

_CONFIG_FILE = os.environ.get("CORE_CONFIG_FILE", "")
_CONFIG = configparser.ConfigParser()

def load_configs(section):
    try:
        with open(_CONFIG_FILE) as c_file:
            _CONFIG.read_file(c_file)

    except FileNotFoundError:
        print("Configuration file not found")
        return None

    return _CONFIG[section] if section in _CONFIG else None