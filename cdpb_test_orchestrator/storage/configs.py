from typing import List

from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

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


def deleteById(db: Session, config_id: int) -> bool:
    selstmt = select(models.Config).where(models.Config.id == config_id)
    existing_project = db.execute(selstmt).scalars().one_or_none()
    if existing_project:
        selstmt = select(models.Config).where(models.Config.id == config_id)
        db.execute(selstmt)
        db.commit()
    else:
        raise NoResultFound

    delstmt = delete(models.Project).where(models.Project.id == config_id)
    db.execute(delstmt)
    db.commit()
    return True


def id2content(db: Session, config_id: int) -> str:
    stmt = select(models.Config.content).where(models.Config.id == config_id)
    return db.execute(stmt).scalars().one()


def project_id2ids(db: Session, project_id: int) -> List[int]:
    stmt = select(models.Config.id).where(models.Config.project_id == project_id)
    with_duplicates = db.execute(stmt).scalars().all()
    return list(set(with_duplicates))
