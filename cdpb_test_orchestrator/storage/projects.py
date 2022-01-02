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
        delstmt = delete(models.Project).where(models.Project.id == project_id)
        db.execute(delstmt)
        db.commit()
    else:
        raise sqlalchemy.exc.NoResultFound
    return True


def id2project(db: Session, project_id: int) -> Project:
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = db.execute(stmt).scalars().one()
    return Project.from_orm(result)


def id2parser(db: Session, project_id: int) -> ResultParser:
    stmt = select(models.Project.parser).where(models.Project.id == project_id)
    parser = db.execute(stmt).scalars().one()
    return ResultParser(parser)
