from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
from test_orchestrator.api.response_bodies import TestResponse

from .sql import models


def add(db: Session, project_id: int, whole_project_test: bool) -> int:
    test = models.TestGroup(project_id, whole_project_test)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test.id


def add_test_to_test_group(
        db: Session,
        test_id: int,
        test_group_id: int) -> None:
    test_in_test_group = models.TestInTestGroup(test_group_id, test_id)
    db.add(test_in_test_group)
    db.commit()
    db.refresh(test_in_test_group)
    return


def get_test_report(db: Session, test_id: int) -> TestResponse:
    test_report = TestResponse(individual_results={
        2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    # TODO IMPLEMENT
    return test_report


def id2exists(db: Session, test_id: int) -> bool:
    stmt = (select(models.TestGroup)
            .where(models.TestGroup.id == test_id))
    test_group = db.execute(stmt).scalars().one_or_none()
    return test_group is not None


def id2finished(db: Session, test_group_id: int) -> bool:
    j = (models.Test
         .join(models.TestInTestGroup,
               models.TestInTestGroup.test_id == models.Test.id))
    stmt = (select(models.Test.finished).select_from(j)
            .where(models.TestInTestGroup.id == test_group_id))
    tests_finished = db.execute(stmt).scalars().all
    return all(tests_finished)
