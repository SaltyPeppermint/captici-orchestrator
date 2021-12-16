from typing import List

from sqlalchemy.orm import Session
from test_orchestrator.api.request_bodies import SelectionStrategy

from .selection_strategies import path_distance


def select_configs(
        db: Session, project_id: int, n_configs: int, strategy: SelectionStrategy) -> List[int]:
    if strategy == SelectionStrategy.PATH_DISTANCE:
        return path_distance.select(db, project_id, n_configs)
