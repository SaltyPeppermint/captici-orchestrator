from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
from test_orchestrator.api.response_bodies import TestResponse

from .sql import models


def add(db: Session, project_id: int, whole_project_test: bool) -> int:
    test = models.Test(project_id, whole_project_test)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test.id


def add_result_to_test(db: Session, test_id: int, result_id: int) -> None:
    result_in_test = models.ResultsInTest(test_id, result_id)
    db.add(result_in_test)
    db.commit()
    db.refresh(result_in_test)
    return


def get_test_report(db: Session, test_id: int) -> TestResponse:
    test_report = TestResponse(individual_results={
        2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    # TODO IMPLEMENT
    return test_report


def id2exists(db: Session, test_id: int) -> bool:
    stmt = (select(models.Test)
            .where(models.Test.id == test_id))
    result = db.execute(stmt).scalars().one_or_none()
    return result is not None


def id2finished(db: Session, test_id: int) -> bool:
    j = (models.Result
         .join(models.ResultsInTest,
               models.ResultsInTest.result_id == models.Result.id))
    stmt = (select(models.Result.finished).select_from(j)
            .where(models.ResultsInTest.test_id == test_id))
    results_finished = db.execute(stmt).scalars().all
    return all(results_finished)
