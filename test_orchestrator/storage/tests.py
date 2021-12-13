from typing import List
from sqlalchemy.orm import Session

from test_orchestrator.api.response_bodies import TestResponse
from .sql import models


def add(db: Session, project_id: int) -> int:
    test = models.Test(project_id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test.id


def get_test_report(db: Session, project_id: int, test_id: int) -> TestResponse:
    test_report = TestResponse(individual_results={
        2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    # TODO IMPLEMENT
    return test_report


def id2exists(db: Session, project_id: int, test_id: int) -> bool:
    test = (db
            .query(models.Test)
            .filter(models.Test.id == test_id)
            .one_or_none())
    return test is not None


def id2finished(db: Session, project_id: int, test_id: int) -> bool:
    results_finished = (db
                        .query(models.Result.finished)
                        .join(
                            models.ResultsInTest,
                            models.ResultsInTest.result_id == models.Result.id
                        )
                        .filter(models.ResultsInTest.test_id == test_id)
                        .all())
    return all(results_finished)
