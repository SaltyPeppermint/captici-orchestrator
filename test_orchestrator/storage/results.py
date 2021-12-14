from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, update

from .sql import models


def id2commit_id(db: Session, result_id: int) -> int:
    stmt = select(models.Result.commit_id).where(models.Result.id == result_id)
    return db.execute(stmt).scalars().one()


def id2content(db: Session, result_id: int) -> int:
    stmt = select(models.Result.content).where(models.Result.id == result_id)
    return db.execute(stmt).scalars().one()


def id2config_id(db: Session, result_id: int) -> int:
    stmt = select(models.Result.config_id).where(models.Result.id == result_id)
    return db.execute(stmt).scalars().one()


def update_preceding(
        db: Session,
        result_id: int,
        preceding_commit_id: str) -> None:

    stmt = (update(models.Result)
            .where(models.Result.id == result_id)
            .values(preceding_commit_id=preceding_commit_id, finished=True))
    db.execute(stmt)
    db.commit()
    return


def update_following(
        db: Session,
        result_id: int,
        following_commit_id: str) -> None:

    stmt = (update(models.Result)
            .where(models.Result.id == result_id)
            .values(following_commit_id=following_commit_id, finished=True))
    db.execute(stmt)
    db.commit()
    return


def mark_as_degradation(db: Session, result_id: int) -> None:
    stmt = (update(models.Result)
            .where(models.Result.id == result_id)
            .values(revelead_cdpb=True, finished=True))
    db.execute(stmt)
    db.commit()
    return


def add_empty(
        db: Session,
        config_id: int,
        commit_id: int,
        preceding_commit_id: int | None,
        following_commit_id: int | None) -> int:

    result = models.Result(config_id, commit_id,
                           preceding_commit_id, following_commit_id)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result.id


def fill_content(db: Session, result_id: int, content: str):
    stmt = (update(models.Result)
            .where(models.Result.id == result_id)
            .values(content=content))
    db.execute(stmt)
    db.commit()
    return

    # class ResultMetadata:
    #     def __init__(self, project_id: int, commit_hash: str, config_id: int):
    #         self.project_id = project_id
    #         self.commit_hash = commit_hash
    #         self.config_id = config_id

    #     def serialize(self) -> str:
    #         return pickle.dumps(self).encode("base64", "strict")

    #     @classmethod
    #     def deserialize(cls, ser_result_metadata):
    #         return cls(pickle.loads(ser_result_metadata.decode("base64", "strict")))

    #     def __iter__(self) -> Iterable:
    #         yield self.project_id
    #         yield self.commit_hash
    #         yield self.config_id

    # def add(ser_result_metadata: str, result_content: str):
    #     project_id, commit_hash, config_id = ResultMetadata.deserialize(
    #         ser_result_metadata)
    #     return True
