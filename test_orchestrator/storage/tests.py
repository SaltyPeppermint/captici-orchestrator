from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, update

from .sql import models


def id2commit_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.commit_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2test_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.result).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2config_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.config_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def update_preceding(
        db: Session,
        test_id: int,
        preceding_commit_id: str) -> None:

    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(preceding_commit_id=preceding_commit_id, finished=True))
    db.execute(stmt)
    db.commit()
    return


def update_following(
        db: Session,
        test_id: int,
        following_commit_id: str) -> None:

    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(following_commit_id=following_commit_id, finished=True))
    db.execute(stmt)
    db.commit()
    return


def mark_as_degradation(db: Session, test_id: int) -> None:
    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(revealed_bug=True, finished=True))
    db.execute(stmt)
    db.commit()
    return


def add_empty(
        db: Session,
        config_id: int,
        commit_id: int,
        preceding_commit_id: int | None,
        following_commit_id: int | None) -> int:

    test = models.Test(config_id, commit_id,
                       preceding_commit_id, following_commit_id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test.id


def add_result(db: Session, test_id: int, result: str):
    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(result=result))
    db.execute(stmt)
    db.commit()
    return
