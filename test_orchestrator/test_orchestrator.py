from fastapi import FastAPI, status
from fastapi.params import Body, Depends, Path, Query
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

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
    result_id: int = Query(...,
                           title="Id of the result to add", gt=0),
    content: str = Body(...,
                        description="Content of the result as string. Max length of 65536 characters.",
                        max_length=65536)):
    storage.results.fill_content(result_id, content)
    return


@app.get("/tars", status_code=status.HTTP_200_OK)
async def request_tar(
        tar_path: str = Query(...,
                              description="Tar_Path",
                              max_length=65536)):
    return FileResponse(tar_path)
