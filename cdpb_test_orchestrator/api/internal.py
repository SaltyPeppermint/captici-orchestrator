# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.params import Body, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
from cdpb_test_orchestrator import storage, cdpb_testing
from cdpb_test_orchestrator.storage.sql.database import get_db

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    responses={404: {"description": "Not found"}},
)


@router.get("/adapter")
async def get_adapter():
    return FileResponse("static/performance-test-adapter")


@router.post("/results", status_code=status.HTTP_200_OK)
async def add_result(
    background_tasks: BackgroundTasks,
    test_id: int = Query(..., title="Id of the test to add to", gt=0),
    test_group_id: int = Query(..., title="Id of the test group", gt=0),
    result: str = Body(
        ...,
        description="Content of the test as string. Max length 65536.",
        max_length=65536,
    ),
    db: Session = Depends(get_db),
):
    storage.cdpb_tests.add_result(db, test_id, result)
    if storage.cdpb_test_groups.id2whole_project_test(db, test_group_id):
        background_tasks.add_task(
            cdpb_testing.cdpb_test.report_action, db, test_group_id, result, test_id
        )
    return


@router.get("/tars", status_code=status.HTTP_200_OK)
async def request_tar(
    tar_path: str = Query(..., description="Tar_Path", max_length=65536)
):
    return FileResponse(tar_path)
