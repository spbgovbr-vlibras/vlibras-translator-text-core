from enum import auto
from enum import Enum


class VideoStatus(Enum):
    QUEUED = auto()
    GENERATING = auto()
    GENERATED = auto()
    FAILED = auto()
    EXPIRED = auto()
