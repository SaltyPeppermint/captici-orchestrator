from typing import List

from api.request_bodies import SelectionStrategy
from sqlalchemy.orm import Session

from .selection_strategies import all, path_distance


def select_configs(
        db: Session, project_id: int, n_configs: int, strategy: SelectionStrategy) -> List[int]:
    if strategy == SelectionStrategy.ALL:
        return all.select(db, project_id, n_configs)
    if strategy == SelectionStrategy.PATH_DISTANCE:
        return path_distance.select(db, project_id, n_configs)
