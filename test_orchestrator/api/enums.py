from enum import Enum


class SelectionStrategy(str, Enum):
    ALL = "all"
    PATH_DISTANCE = "path_distance"
