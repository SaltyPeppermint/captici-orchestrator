# APIRouter creates path operations for item module
from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path, Query

from test_orchestrator import testing
from test_orchestrator import storage


router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)


@router.post("/commit/{project_id}", status_code=status.HTTP_200_OK)
async def request_commit_test(project_id: int = Path(..., title="Id of the project to test", gt=0),
                              commit: str = Query(...,
                                                  description="SHA1 Hash of the new commit to test. Tags or anything else are not accepted. Has to be a hexadecimal string of length 40.", min_length=40, max_length=40, regex=r"[0-9A-Fa-f]+")):
    test_id = commit.test(project_id, commit)
    return {"test_id": test_id}


@router.get("/commit/{project_id}", response_model=storage.Report, status_code=status.HTTP_200_OK)
async def read_commit_test_result(project_id: int = Path(..., title="Id of the tested project", gt=0),
                                  test_id: int = Query(..., title="Result id of the test", gt=0)):
    if not testing.commit.does_test_exist(project_id, test_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    elif not testing.commit.is_test_finished(project_id, test_id):
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                            detail="Test not ready")
    else:
        return storage.reports.get_test_report(project_id, test_id)


@router.post("/project/{project_id}", status_code=status.HTTP_200_OK)
async def request_project_test(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    test_id = testing.project.test(project_id)
    return {"test_id": test_id}


@router.get("/project/{project_id}")
async def read_project_test_status(project_id: int = Path(..., title="Id of the tested project", gt=0),
                                   test_id: int = Query(..., title="Result id of the test", gt=0)):
    if not testing.project.does_test_exist(project_id):
        raise HTTPException(status_code=404, detail="Item not found")
    elif not testing.project.is_test_finished(project_id):
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                            detail="Test not ready")
    else:
        return storage.reports.get_test_report(project_id, test_id)
