from enum import Enum
from typing import List
from sqlalchemy.orm import Session

from test_orchestrator.api.request_bodies import RegisterRequest
from .sql import models
from . import results, configs, repositories


def add(db: Session, register_req: RegisterRequest) -> int:
    project = models.Project(register_req)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.id


def delete(db: Session, project_id: int) -> bool:
    (db
        .query(models.Project)
        .filter(models.Project.id == project_id)
        .delete())
    return True


def id2name(db: Session, project_id: int) -> str:
    return (db
            .query(models.Project.name)
            .filter(models.Project.id == project_id)
            .one())


def id2tester_command(db: Session, project_id: int) -> str:
    return (db
            .query(models.Project.tester_command)
            .filter(models.Project.id == project_id)
            .one())
    # return "cd /app && python3 -m pytest --junitxml=/tmp/report"


def id2result_ids(db: Session, project_id: int) -> List[int]:
    # SELECT config, commit FROM results JOIN commits where project_id = project_id
    return (db
            .query(models.Result.id)
            .join(
                models.Commit,
                models.Commit.id == models.Result.commit_id
            )
            .join(
                models.Project,
                models.Project.id == models.Commit.project_id
            )
            .filter(models.Project.id == project_id)
            .all())


def id2configs(db: Session, project_id: int) -> List[int]:
    return (db
            .query(models.Config.id)
            .join(
                models.Project,
                models.Project.id == models.Config.project_id
            )
            .filter(models.Project.id == project_id)
            .all())
