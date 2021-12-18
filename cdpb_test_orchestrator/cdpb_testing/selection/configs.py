from typing import List, Tuple

from sqlalchemy.orm import Session
from cdpb_test_orchestrator.api.request_bodies import SelectionStrategy

from .selection_strategies import path_distance


def select_configs(
    db: Session,
    project_id: int,
    n_configs: int,
    tests_with_bugs: List[int],
    strategy: SelectionStrategy,
) -> List[Tuple[float, int]]:

    if strategy == SelectionStrategy.PATH_DISTANCE:
        return path_distance.select(db, project_id, n_configs, tests_with_bugs)
    else:
        raise AttributeError("Strategy not supported.")
