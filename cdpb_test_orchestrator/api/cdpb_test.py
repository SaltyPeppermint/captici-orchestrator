# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604

from cdpb_test_orchestrator import cdpb_testing, storage
from cdpb_test_orchestrator.data_objects import (
    CommitTestRequest,
    ProjectTestRequest,
    TestResponse,
)
from cdpb_test_orchestrator.storage.sql.database import get_db
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.params import Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)


@router.post("/commit", status_code=status.HTTP_200_OK)
def request_commit_test(
    testing_req: CommitTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    test_group_id = storage.cdpb_test_groups.add(
        db, testing_req.project_id, testing_req.threshold, False
    )
    background_tasks.add_task(
        cdpb_testing.cdpb_test.test_commit,
        db,
        test_group_id,
        testing_req,
    )
    return {"test_group_id": test_group_id}


@router.post("/project", status_code=status.HTTP_200_OK)
def request_project_test(
    testing_req: ProjectTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    test_group_id = storage.cdpb_test_groups.add(
        db, testing_req.project_id, testing_req.threshold, True
    )
    background_tasks.add_task(
        cdpb_testing.cdpb_test.test_whole_project,
        db,
        test_group_id,
        testing_req,
    )
    return {"test_group_id": test_group_id}


@router.get("/report", response_model=TestResponse, status_code=status.HTTP_200_OK)
def read_test_report(
    test_group_id: int = Query(..., title="(Id of the test_group", gt=0),
    db: Session = Depends(get_db),
):
    if not storage.cdpb_test_groups.id2exists(db, test_group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found"
        )
    elif not storage.cdpb_test_groups.id2finished(db, test_group_id):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, detail="Test not ready"
        )
    else:
        return cdpb_testing.evaluate.testing_report(db, test_group_id)
