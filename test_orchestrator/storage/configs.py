from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .sql import models


def add(db: Session, project_id: int, content: str) -> int:
    config = models.Config(project_id, content)
    db.add(config)
    db.commit()
    db.refresh(config)
    if config.id:
        return config.id
    else:
        raise SQLAlchemyError


def id2content(db: Session, config_id: int) -> str:
    stmt = (select(models.Config.content)
            .where(models.Config.id == config_id))
    return db.execute(stmt).scalars().one()


def project_id2ids(db: Session, project_id: int) -> List[int]:
    stmt = (select(models.Config.id)
            .where(models.Config.project_id == project_id))
    with_duplicates = db.execute(stmt).scalars().all()
    return list(set(with_duplicates))
