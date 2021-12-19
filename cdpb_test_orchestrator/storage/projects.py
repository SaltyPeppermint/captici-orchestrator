from typing import Tuple

import sqlalchemy
from cdpb_test_orchestrator.data_objects import Project, ResultParser
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

from .sql import models


def add(db: Session, project_to_add: Project) -> int:
    project = models.Project(project_to_add)
    db.add(project)
    db.commit()
    db.refresh(project)
    if project.id:
        return project.id
    else:
        raise SQLAlchemyError("Could not insert project.")


def deleteById(db: Session, project_id: int) -> bool:
    selstmt = select(models.Project).where(models.Project.id == project_id)
    existing_project = db.execute(selstmt).scalars().one_or_none()
    if existing_project:
        selstmt = select(models.Project).where(models.Project.id == project_id)
        db.execute(selstmt)
        db.commit()
    else:
        raise sqlalchemy.exc.NoResultFound

    delstmt = delete(models.Project).where(models.Project.id == project_id)
    db.execute(delstmt)
    db.commit()
    return True


def id2project(db: Session, project_id: int) -> Project:
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = db.execute(stmt).scalars().one()
    return Project.from_orm(result)


def id2name(db: Session, project_id: int) -> str:
    stmt = select(models.Project.name).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()


def id2result_path(db: Session, project_id: int) -> str:
    stmt = select(models.Project.result_path).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()


def id2tester_image(db: Session, project_id: int) -> str:
    stmt = select(models.Project.tester_image).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()


def id2is_two_container(db: Session, project_id: int) -> str:
    stmt = select(models.Project.two_container).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()


def id2config_path(db: Session, project_id: int) -> str:
    stmt = select(models.Project.config_path).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()


def id2tester_command(db: Session, project_id: int) -> str:
    stmt = select(models.Project.tester_command).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()
    # return "cd /app && python3 -m pytest --junitxml=/tmp/report"


def id2git_info(db: Session, project_id: int) -> Tuple[str, str, str]:
    stmt = select(
        models.Project.repo_url, models.Project.git_user, models.Project.auth_token
    ).where(models.Project.id == project_id)
    return db.execute(stmt).scalars().one()
    # return ("github.com/BurntSushi/ripgrep.git", "git", "")


def id2parser(db: Session, project_id: int) -> ResultParser:
    stmt = select(models.Project.parser).where(models.Project.id == project_id)
    parser = db.execute(stmt).scalars().one()
    return ResultParser(parser)
