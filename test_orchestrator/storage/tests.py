from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, update

from .sql import models


def id2commit_hash(db: Session, test_id: int) -> int:
    stmt = select(models.Test.commit_hash).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2config_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.config_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2result(db: Session, test_id: int) -> int:
    stmt = select(models.Test.result).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def id2preceding_commit_hash(db: Session, test_id: int) -> str | None:
    stmt = (select(models.Test.preceding_commit_hash)
            .where(models.Test.id == test_id))
    return db.execute(stmt).scalars().one_or_none()


def id2following_commit_hash(db: Session, test_id: int) -> str | None:
    stmt = (select(models.Test.following_commit_hash)
            .where(models.Test.id == test_id))
    return db.execute(stmt).scalars().one_or_none()


def id2project_id(db: Session, test_id: int) -> int:
    stmt = select(models.Test.project_id).where(models.Test.id == test_id)
    return db.execute(stmt).scalars().one()


def config_id_and_hash2result(
        db: Session,
        config_id: int,
        commit_hash: str) -> int:
    stmt = (select(models.Test.result)
            .where(models.Test.config_id == config_id)
            .where(models.Test.commit_hash == commit_hash))
    return db.execute(stmt).scalars().one()


def config_id_and_hash2id(
        db: Session,
        config_id: int,
        commit_hash: str) -> int:
    stmt = (select(models.Test.id)
            .where(models.Test.config_id == config_id)
            .where(models.Test.commit_hash == commit_hash))
    return db.execute(stmt).scalars().one()


def project_id2test_ids(db: Session, project_id: int) -> List[int]:
    stmt = (select(models.Test.id).where(models.Test.id == project_id))
    return db.execute(stmt).scalars().all()


def update_preceding(
        db: Session,
        test_id: int,
        preceding_commit_hash: str) -> None:

    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(preceding_commit_hash=preceding_commit_hash, finished=True))
    db.execute(stmt)
    db.commit()
    return


def update_following(
        db: Session,
        test_id: int,
        following_commit_hash: str) -> None:

    stmt = (update(models.Test)
            .where(models.Test.id == test_id)
            .values(following_commit_hash=following_commit_hash, finished=True))
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
        commit_hash: int,
        preceding_commit_hash: Optional[str],
        following_commit_hash: Optional[str]) -> int:

    test = models.Test(config_id, commit_hash,
                       preceding_commit_hash, following_commit_hash)
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
