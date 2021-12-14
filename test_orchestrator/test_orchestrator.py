from fastapi import FastAPI, status
from fastapi.params import Body, Depends, Path
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

from . import api, storage
from .storage.sql.database import get_db

app = FastAPI()
app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.test.router)


@app.get("/adapter")
async def get_adapter():
    return FileResponse("static/performance-test-adapter")


@app.post("/results/{result_id}", status_code=status.HTTP_200_OK)
async def add_result(
    result_id: int = Path(...,
                          title="Id of the result to add", gt=0),
    content: str = Body(...,
                        description="Content of the result as string. Max length of 65536 characters.",
                        max_length=65536)):
    storage.results.fill_content(result_id, content)
    return


@app.get("/tars/{ser_tar_metadata}", status_code=status.HTTP_200_OK)
async def request_tar(
        ser_tar_metadata: str = Path(...,
                                     description="Serialized Tar Metadata. Max length of 65536 characters.",
                                     max_length=65536),
        db: Session = Depends(get_db)):
    tar_path = storage.tars.serialized2tar_path(db, ser_tar_metadata)
    return FileResponse(tar_path)
