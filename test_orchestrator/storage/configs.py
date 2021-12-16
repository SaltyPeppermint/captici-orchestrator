from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .sql import models


def id2test_ids(db: Session, config_id: int) -> List[int]:
    stmt = (select(models.Test.id)
            .where(models.Test.config_id == config_id))
    with_duplicates = db.execute(stmt).scalars().all()
    return list(set(with_duplicates))


def add(db: Session, project_id: int, content: str) -> int:
    config = models.Config(project_id, content)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config.id


def id2content(db: Session, config_id: int) -> str:
    stmt = (select(models.Config.content)
            .where(models.Config.id == config_id))
    return db.execute(stmt).scalars().one()
