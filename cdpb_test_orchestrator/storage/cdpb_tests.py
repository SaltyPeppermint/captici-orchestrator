from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, update

from .sql import models


def id2commit_hash(db: Session, test_id: int) -> str:
    stmt = select(models.CDPBTest.commit_hash).where(models.CDPBTest.id == test_id)
    return db.execute(stmt).scalars().one()


def id2config_id(db: Session, test_id: int) -> int:
    stmt = select(models.CDPBTest.config_id).where(models.CDPBTest.id == test_id)
    return db.execute(stmt).scalars().one()


def id2result(db: Session, test_id: int) -> str | None:
    stmt = select(models.CDPBTest.result).where(models.CDPBTest.id == test_id)
    return db.execute(stmt).scalars().one_or_none()


def id2preceding_id(db: Session, test_id: int) -> int | None:
    stmt = select(models.CDPBTest.preceding_test_id).where(
        models.CDPBTest.id == test_id
    )
    return db.execute(stmt).scalars().one_or_none()


def id2following_id(db: Session, test_id: int) -> int | None:
    stmt = select(models.CDPBTest.following_test_id).where(
        models.CDPBTest.id == test_id
    )
    return db.execute(stmt).scalars().one_or_none()


def id2project_id(db: Session, test_id: int) -> int:
    stmt = select(models.CDPBTest.project_id).where(models.CDPBTest.id == test_id)
    return db.execute(stmt).scalars().one()


def project_id2ids(db: Session, project_id: int) -> List[int]:
    stmt = select(models.CDPBTest.id).where(models.CDPBTest.project_id == project_id)
    return db.execute(stmt).scalars().all()


def update_preceding(db: Session, test_id: int, preceding_test_id: int) -> None:
    stmt = (
        update(models.CDPBTest)
        .where(models.CDPBTest.id == test_id)
        .values(preceding_test_id=preceding_test_id)
    )
    db.execute(stmt)
    db.commit()
    return


def update_following(db: Session, test_id: int, following_test_id: int) -> None:
    stmt = (
        update(models.CDPBTest)
        .where(models.CDPBTest.id == test_id)
        .values(following_test_id=following_test_id)
    )
    db.execute(stmt)
    db.commit()
    return


def add_empty(
    db: Session,
    project_id: int,
    config_id: int,
    commit_hash: str,
    preceding_test_id: int | None,
    following_test_id: int | None,
) -> int:
    test = models.CDPBTest(
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
    stmt = (
        update(models.CDPBTest)
        .where(models.CDPBTest.id == test_id)
        .values(result=result)
    )
    db.execute(stmt)
    db.commit()
    return
