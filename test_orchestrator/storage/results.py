from sqlalchemy.orm import Session

from .sql import models


def id2commit_id(db: Session, result_id: int) -> int:
    return (db
            .query(models.Result.commit_id)
            .filter(models.Result.id == result_id)
            .one())


def id2content(db: Session, result_id: int) -> int:
    return (db
            .query(models.Result.content)
            .filter(models.Result.id == result_id)
            .one())


def id2config_id(db: Session, result_id: int) -> int:
    return (db
            .query(models.Result.config_id)
            .filter(models.Result.id == result_id)
            .one())


def add_empty(db: Session, config_id: int, commit_id: int) -> int:
    result = models.Result(config_id, commit_id)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result.id


def fill_content(db: Session, result_id: int, content: str):
    result = (db
              .query(models.Result)
              .filter(models.Result.id == result_id)
              .one_or_none())
    result.content = content
    db.commit()
    db.refresh(result)
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
