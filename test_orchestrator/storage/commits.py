from typing import List
from sqlalchemy.orm import Session
from .sql import models


def id2hash(db: Session, commit_id: int) -> str:
    return (db
            .query(models.Commit.hash)
            .filter(models.Commit.id == commit_id)
            .one())
