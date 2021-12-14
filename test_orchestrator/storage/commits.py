from typing import List
from sqlalchemy.orm import Session

from .sql import models


def id2hash(db: Session, commit_id: int) -> str:
    return (db
            .query(models.Commit.commit_hash)
            .filter(models.Commit.id == commit_id)
            .one())


def add_or_update(db: Session, project_id: int, commit_hash: str) -> int:
    existing_commit = (db
                       .query(models.Commit)
                       .filter(
                           models.Commit.project_id == project_id,
                           models.Commit.commit_hash == commit_hash
                       )
                       .one_or_none())
    if existing_commit:
        return existing_commit.id
    else:
        new_commit = models.Commit(project_id, commit_hash, False)
        db.add(new_commit)
        db.commit()
        db.refresh(new_commit)
        return new_commit.id
