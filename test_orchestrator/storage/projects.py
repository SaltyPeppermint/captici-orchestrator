from typing import List, Tuple
import sqlalchemy

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select, join
from test_orchestrator.api.request_bodies import RegisterRequest

from .sql import models


def add(db: Session, req: RegisterRequest) -> int:
    project = models.Project(req.name,
                             req.tester_command,
                             req.repo_url,
                             req.git_user,
                             req.auth_token,
                             req.main_branch,
                             req.config_path,
                             req.two_container,
                             req.tester_image,
                             req.email)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.id


def deleteById(db: Session, project_id: int) -> bool:
    stmt = (select(models.Project)
            .where(models.Project.id == project_id))
    result = db.execute(stmt).scalars().one_or_none()
    if result:
        stmt = (select(models.Project)
                .where(models.Project.id == project_id))
        db.execute(stmt)
        db.commit()
    else:
        raise sqlalchemy.exc.NoResultFound

    stmt = (delete(models.Project)
            .where(models.Project.id == project_id))
    db.execute(stmt)
    db.commit()
    return True


def id2name(db: Session, project_id: int) -> str:
    stmt = (select(models.Project.name)
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()


def id2tester_image(db: Session, project_id: int) -> str:
    stmt = (select(models.Project.tester_image)
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()


def id2is_two_container(db: Session, project_id: int) -> str:
    stmt = (select(models.Project.two_container)
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()


def id2config_path(db: Session, project_id: int) -> str:
    stmt = (select(models.Project.config_path)
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()


def id2tester_command(db: Session, project_id: int) -> str:
    stmt = (select(models.Project.tester_command)
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()
    # return "cd /app && python3 -m pytest --junitxml=/tmp/report"


def id2git_info(db: Session, project_id: int) -> Tuple[str, str, str]:
    stmt = (select(models.Project.repo_url,
                   models.Project.git_user,
                   models.Project.auth_token
                   )
            .where(models.Project.id == project_id))
    return db.execute(stmt).scalars().one()
    # return ("github.com/BurntSushi/ripgrep.git", "git", "")


def id2result_ids(db: Session, project_id: int) -> List[int]:
    # SELECT config, commit FROM results JOIN commits where project_id = project_id
    j = join(models.Commit, models.Result,
             models.Commit.id == models.Result.commit_id)
    stmt = (select(models.Result.config_id).select_from(j)
            .where(models.Commit.project_id == project_id))
    with_duplicates = db.execute(stmt).scalars().all()
    return list(set(with_duplicates))


def id2config_ids(db: Session, project_id: int) -> List[int]:
    stmt = (select(models.Config.id)
            .where(models.Config.project_id == project_id))
    with_duplicates = db.execute(stmt).scalars().all()
    return list(set(with_duplicates))
