from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
from test_orchestrator.api.response_bodies import TestResponse

from .sql import models


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


def id2finished(db: Session, test_group_id: int) -> bool:
    j = (models.Test
         .join(models.TestInTestGroup,
               models.TestInTestGroup.test_id == models.Test.id))
    stmt = (select(models.Test.finished).select_from(j)
            .where(models.TestInTestGroup.id == test_group_id))
    tests_finished = db.execute(stmt).scalars().all
    return all(tests_finished)


def test_id2id(db: Session, test_id: int) -> int:
    stmt = (select(models.TestInTestGroup.test_group_id)
            .where(models.TestInTestGroup.test_id == test_id))
    return db.execute(stmt).scalars().one()
