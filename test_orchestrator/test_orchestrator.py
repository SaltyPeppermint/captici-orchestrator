from starlette.responses import FileResponse
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Path, Query

from test_orchestrator import storage
from test_orchestrator import api


app = FastAPI()
app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.test.router)


@app.get("/adapter")
async def get_adapter():
    return FileResponse("static/performance-test-adapter")


@app.post("/results/{result_id}", status_code=status.HTTP_200_OK)
async def request_project_test(
    result_id: int = Path(...,
                          title="Id of the result to add", gt=0),
    content: str = Body(...,
                        description="Content of the result as string. Max length of 65536 characters.",
                        max_length=65536)):
    storage.results.add(result_id, content)
    return


@app.get("/tars/{ser_tar_metadata}", status_code=status.HTTP_200_OK)
async def request_tar(
    ser_tar_metadata: str = Path(...,
                                 description="Serialized Tar Metadata. Max length of 65536 characters.",
                                 max_length=65536)):
    tar_path = storage.tars.serialized2tar_path(ser_tar_metadata)
    return FileResponse(tar_path)
