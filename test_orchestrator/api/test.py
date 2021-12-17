# APIRouter creates path operations for item module
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.params import Body, Depends, Query
from sqlalchemy.orm import Session
from test_orchestrator import storage, testing
from test_orchestrator.storage.sql.database import get_db

from .request_bodies import CommitTestRequest, ProjectTestRequest
from .response_bodies import TestResponse

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)


@router.post("/commit", status_code=status.HTTP_200_OK)
async def request_commit_test(
        background_tasks: BackgroundTasks,
        project_id: int = Query(..., title="Project_id to test", gt=0),
        testing_request: CommitTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_group_id = storage.test_groups.add(
        db, project_id, testing_request.threshold, False)
    background_tasks.add_task(
        testing.test.test_commit,
        db, project_id, test_group_id, testing_request)

    return {"test_group_id": test_group_id}


@router.post("/project", status_code=status.HTTP_200_OK)
async def request_project_test(
        background_tasks: BackgroundTasks,
        project_id: int = Query(..., title="Project_id to test", gt=0),
        testing_request: ProjectTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_group_id = storage.test_groups.add(
        db, project_id, testing_request.threshold, True)
    background_tasks.add_task(
        testing.test.test_whole_project,
        db, project_id, test_group_id, testing_request)

    return {"test_group_id": test_group_id}


@ router.get("/report", response_model=TestResponse, status_code=status.HTTP_200_OK)
async def read_test_report(
        test_group_id: int = Query(..., title="(Id of the test_group", gt=0),
        db: Session = Depends(get_db)):

    if not storage.test_groups.id2exists(db, test_group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    elif not storage.test_groups.id2finished(db, test_group_id):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Test not ready"
        )
    else:
        return testing.evaluate.testing_report(db, test_group_id)
