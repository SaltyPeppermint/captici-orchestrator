# APIRouter creates path operations for item module
from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Depends, Path, Query
from sqlalchemy.orm import Session
from test_orchestrator import storage, testing
from test_orchestrator.storage.sql.database import get_db

from .request_bodies import CommitTestRequest
from .response_bodies import TestResponse

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)


@router.post("/project", status_code=status.HTTP_200_OK)
async def request_commit_test(
        project_id: int = Query(..., title="Project_id to test", gt=0),
        testing_request: CommitTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_id = testing.commit.test_single_commit(
        db, project_id, testing_request)
    return {"test_id": test_id}


@router.post("/commit", status_code=status.HTTP_200_OK)
async def request_commit_test(
        project_id: int = Query(..., title="Project_id to test", gt=0),
        testing_request: CommitTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_id = testing.commit.test_multiple_commits(
        db, project_id, testing_request)
    return {"test_id": test_id}


@router.get("/report", response_model=TestResponse, status_code=status.HTTP_200_OK)
async def read_test_report(
        test_id: int = Query(..., title="(Id of the test", gt=0),
        db: Session = Depends(get_db)):

    if not storage.test_groups.id2exists(db, test_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    elif not storage.test_groups.id2finished(db, test_id):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Test not ready"
        )
    else:
        return storage.test_groups.get_test_report(test_id)
