from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .sql import models


def id2hash(db: Session, commit_id: int) -> str:
    stmt = (select(models.Commit.commit_hash)
            .where(models.Commit.id == commit_id))
    return db.execute(stmt).scalars().one()


def add_or_get(db: Session, project_id: int, commit_hash: str) -> int:
    stmt = (select(models.Commit)
            .filter(models.Commit.project_id == project_id,
                    models.Commit.commit_hash == commit_hash))
    result = db.execute(stmt).scalars().one_or_none()
    if result:
        return result.id
    else:
        commit = models.Commit(project_id, commit_hash, False)
        db.add(commit)
        db.commit()
        db.refresh(commit)
        return commit.id
