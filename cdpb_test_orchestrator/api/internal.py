# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
import logging

from cdpb_test_orchestrator import cdpb_testing, storage
from cdpb_test_orchestrator.data_objects import Test
from cdpb_test_orchestrator.storage.sql.database import get_db
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.params import Body, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

logger = logging.getLogger("uvicorn")

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    responses={404: {"description": "Not found"}},
)


@router.get("/adapter")
def get_adapter():
    logger.info("Downloading adapter for test.")
    return FileResponse("static/adapter")


@router.post("/result", status_code=status.HTTP_200_OK)
def add_result(
    background_tasks: BackgroundTasks,
    test_id: int = Body(..., title="Id of the test to add to", gt=0),
    test_group_id: int = Body(..., title="Id of the test group", gt=0),
    result: str = Body(
        ..., description="Config as a string. Max length 4096.", max_length=4096
    ),
    db: Session = Depends(get_db),
):
    logger.info("Received result:" + result)
    storage.cdpb_tests.add_result(db, test_id, result)
    if storage.cdpb_test_groups.id2whole_project_test(db, test_group_id):
        config_id = storage.cdpb_tests.id2config_id(db, test_id)
        test = Test(
            id=test_id,
            result=result,
            commit_hash=storage.cdpb_tests.id2commit_hash(db, test_id),
            config_id=config_id,
            config_content=storage.configs.id2content(db, config_id),
            project=storage.projects.id2project(
                db, storage.cdpb_tests.id2project_id(db, test_id)
            ),
        )
        background_tasks.add_task(
            cdpb_testing.cdpb_test.report_action, db, test_group_id, test
        )
    return


@router.get("/tars", status_code=status.HTTP_200_OK)
def request_tar(tar_path: str = Query(..., description="Tar_Path", max_length=65536)):
    return FileResponse(tar_path)
