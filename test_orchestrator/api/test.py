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


@router.post("/project/{project_id}", status_code=status.HTTP_200_OK)
async def request_commit_test(
        project_id: int = Path(..., title="Project_id to test", gt=0),
        testing_request: CommitTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_id = testing.commit.test_single_commit(
        db, project_id, testing_request)
    return {"test_id": test_id}


@router.post("/commit/{project_id}", status_code=status.HTTP_200_OK)
async def request_commit_test(
        project_id: int = Path(..., title="Project_id to test", gt=0),
        testing_request: CommitTestRequest = Body(...),
        db: Session = Depends(get_db)):

    test_id = testing.commit.test_multiple_commits(
        db, project_id, testing_request)
    return {"test_id": test_id}


@router.get("/commit/{project_id}", response_model=TestResponse, status_code=status.HTTP_200_OK)
async def read_test_report(
        project_id: int = Path(..., title="Id of the tested project", gt=0),
        test_id: int = Query(..., title="(Id of the test", gt=0),
        db: Session = Depends(get_db)):

    if not storage.tests.id2exists(db, project_id, test_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    elif not storage.tests.id2finished(project_id, test_id):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Test not ready"
        )
    else:
        return storage.tests.get_test_report(project_id, test_id)


# @router.post("/project/{project_id}", status_code = status.HTTP_200_OK)
# async def request_project_test(
#         project_id: int = Path(..., title="Id of the project to test", gt=0)):

#     test_id=testing.project.test(project_id)
#     return {"test_id": test_id}


# @router.get("/project/{project_id}")
# async def read_project_test_status(
#         project_id: int = Path(..., title="Id of the tested project", gt=0),
#         test_id: int = Query(..., title="Result id of the test", gt=0)):

#     if not testing.project.does_test_exist(project_id):
#         raise HTTPException(status_code = 404, detail = "Item not found")
#     elif not testing.project.is_test_finished(project_id):
#         raise HTTPException(status_code = status.HTTP_202_ACCEPTED,
#                             detail = "Test not ready")
#     else:
#         return storage.reports.get_test_report(project_id, test_id)
