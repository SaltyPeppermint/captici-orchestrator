from fastapi import FastAPI, status
from fastapi.params import Body, Depends, Path, Query
from sqlalchemy.orm.session import Session
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

from test_orchestrator import testing

from . import api, storage
from .settings import config
from .storage.sql.database import get_db

app = FastAPI()
app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.test.router)


@app.get("/adapter")
async def get_adapter():
    return FileResponse("static/performance-test-adapter")


@app.post("/results", status_code=status.HTTP_200_OK)
async def add_result(
        background_tasks: BackgroundTasks,
        test_id: int = Query(...,
                             title="Id of the test to add to", gt=0),
        test_group_id: int = Query(...,
                                   title="Id of the test group", gt=0),
        result: str = Body(...,
                           description="Content of the test as string. Max length of 65536 characters.",
                           max_length=65536),
        db: Session = Depends(get_db)):
    storage.tests.add_result(db, test_id, result)
    if storage.test_groups.id2whole_project_test(db, test_group_id):
        background_tasks.add_task(
            testing.evaluate.report_action,
            db, test_group_id, result, test_id)
    return


@app.get("/tars", status_code=status.HTTP_200_OK)
async def request_tar(
        tar_path: str = Query(...,
                              description="Tar_Path",
                              max_length=65536)):
    return FileResponse(tar_path)
