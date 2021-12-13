from typing import List
from sqlalchemy.orm import Session

from .sql import models


def id2result_ids(db: Session, config_id: int) -> List[int]:
    return (db
            .query(models.Result.id)
            .filter(models.Result.config_id == config_id)
            .all())


def store(db: Session, project_id: int, content: str) -> int:
    config = models.Config(project_id, content)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config.id


def id2content(db: Session, config_id: int) -> str:
    return (db
            .query(models.Config.content)
            .filter(models.Config.id == config_id)
            .one())
