from typing import List

from sqlalchemy.orm import Session
from test_orchestrator import storage


def select(db: Session, project_id: int, n_configs: int) -> List[int]:
    print("Ignoring number and returning all configs")
    return storage.configs.project_id2ids(db, project_id)
