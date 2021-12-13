from enum import Enum
from os import path
from typing import List

from test_orchestrator import storage
from .selection_strategies import all, path_distance


class SelectionStrategy(str, Enum):
    ALL = "all"
    PATH_DISTANCE = "path_distance"


def select_configs(
        project_id: int, n_configs: int, strategy: SelectionStrategy) -> List[int]:
    if strategy == SelectionStrategy.ALL:
        return all.select(project_id, n_configs)
    if strategy == SelectionStrategy.PATH_DISTANCE:
        return path_distance.select(project_id, n_configs)
