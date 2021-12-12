from starlette.responses import FileResponse
from fastapi import FastAPI, BackgroundTasks, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Path, Query
from concurrent.futures.process import ProcessPoolExecutor

from test_orchestrator import storage
from test_orchestrator import api

from test_orchestrator import parallelism

app = FastAPI()
app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.test.router)


@app.on_event("startup")
async def startup_event():
    app.state.executor = parallelism.global_executor


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()


@app.get("/adapter")
async def get_adapter():
    return FileResponse("static/performance-test-adapter")


@app.post("/reports/{report_id}", status_code=status.HTTP_200_OK)
async def request_project_test(report_id: str = Path(...,
                                                     description="Identifier of the report as string. Max length of 65536 characters.",
                                                     max_length=1000),
                               content: str = Body(...,
                                                   description="Content of the report as string. Max length of 65536 characters.",
                                                   max_length=65536)):
    storage.reports.add(report_id, content)
    return


@app.get("/tars/{tar_id}", status_code=status.HTTP_200_OK)
async def request_project_test(report_id: str = Path(...,
                                                     description="Identifier of the report as string. Max length of 65536 characters.",
                                                     max_length=1000)):
    tar_path = storage.tars.id2tar_path(report_id)
    return FileResponse(tar_path)
