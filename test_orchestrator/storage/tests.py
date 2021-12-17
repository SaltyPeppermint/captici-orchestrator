from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import select, update

from .sql import models


def id2commit_hash(db: Session, test_id: int) -> str:
    stmt = select(models.Test.commit_hash).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2config_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.config_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2result(db: Session, test_id: int) -> str:
    stmt = select(models.Test.result).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2preceding_id(db: Session, test_id: int) -> int | None:
    stmt = select(models.Test.preceding_test_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one_or_none()


def id2following_id(db: Session, test_id: int) -> int | None:
    stmt = select(models.Test.following_test_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one_or_none()


def id2project_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.project_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def project_id2ids(db: Session, project_id: int) -> List[int]:
    stmt = select(models.Test.id).where(models.Test.id == project_id)
    return db.execute(stmt).scalars().all()


def update_preceding(db: Session, test_id: int, preceding_commit_hash: str) -> None:
    stmt = (
        update(models.Test)
        .where(models.Test.id == test_id)
        .values(preceding_commit_hash=preceding_commit_hash, finished=True)
    )
    db.execute(stmt)
    db.commit()
    return


def update_following(db: Session, test_id: int, following_commit_hash: str) -> None:
    stmt = (
        update(models.Test)
        .where(models.Test.id == test_id)
        .values(following_commit_hash=following_commit_hash, finished=True)
    )
    db.execute(stmt)
    db.commit()
    return


def mark_as_degradation(db: Session, test_id: int) -> None:
    stmt = (
        update(models.Test)
        .where(models.Test.id == test_id)
        .values(revealed_bug=True, finished=True)
    )
    db.execute(stmt)
    db.commit()
    return


def add_empty(
    db: Session,
    project_id: int,
    config_id: int,
    commit_hash: str,
    preceding_test_id: Optional[int],
    following_test_id: Optional[int],
) -> int:
    test = models.Test(
        project_id, config_id, commit_hash, preceding_test_id, following_test_id
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    if test.id:
        return test.id
    else:
        raise SQLAlchemyError("Could not insert test")


def add_result(db: Session, test_id: int, result: str):
    stmt = update(models.Test).where(models.Test.id == test_id).values(result=result)
    db.execute(stmt)
    db.commit()
    return
