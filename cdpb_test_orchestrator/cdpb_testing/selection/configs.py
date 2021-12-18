from typing import Dict, List, Tuple

from cdpb_test_orchestrator.data_objects import Project, SelectionStrategy

from .selection_strategies import path_distance


def select_configs(
    project: Project,
    n_configs: int,
    bug_dict: Dict[int, str],
    strategy: SelectionStrategy,
) -> List[Tuple[float, int]]:

    if strategy == SelectionStrategy.PATH_DISTANCE:
        return path_distance.select(project, n_configs, bug_dict)
    else:
        raise AttributeError("Strategy not supported.")
