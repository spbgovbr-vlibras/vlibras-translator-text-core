from enum import auto
from enum import Enum


class VideoStatus(Enum):
    QUEUED = auto()
    PROCESSING = auto()
    GENERATED = auto()
    FAILED = auto()
    EXPIRED = auto()
