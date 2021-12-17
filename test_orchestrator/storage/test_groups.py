from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import join, select

from .sql import models


def add(
        db: Session,
        project_id: int,
        threshold: float,
        whole_project_test: bool) -> int:

    test = models.TestGroup(
        project_id,
        threshold,
        whole_project_test)

    db.add(test)
    db.commit()
    db.refresh(test)
    if test.id:
        return test.id
    else:
        raise SQLAlchemyError("Could not insert test.")


def id2threshold(db: Session, test_group_id: int) -> float:
    stmt = (select(models.TestGroup.threshold)
            .where(models.TestGroup.id == test_group_id))
    return db.execute(stmt).scalars().one()


def id2project_id(db: Session, test_result_id: int) -> float:
    stmt = (select(models.TestGroup.project_id)
            .where(models.TestGroup.id == test_result_id))
    return db.execute(stmt).scalars().one()


def id2whole_project_test(db: Session, test_result_id: int) -> bool:
    stmt = (select(models.TestGroup.whole_project_test)
            .where(models.TestGroup.id == test_result_id))
    return db.execute(stmt).scalars().one()


def id2exists(db: Session, test_id: int) -> bool:
    stmt = (select(models.TestGroup)
            .where(models.TestGroup.id == test_id))
    test_group = db.execute(stmt).scalars().one_or_none()
    return test_group is not None


def id2finished(db: Session, test_group_id: int) -> bool:
    j = join(models.Test, models.TestInTestGroup,
             models.TestInTestGroup.test_id == models.Test.id)
    stmt = (select(models.Test.finished).select_from(j)
            .where(models.TestInTestGroup.test_group_id == test_group_id))
    tests_finished = db.execute(stmt).scalars().all()
    return all(tests_finished)
