from starlette.responses import FileResponse
import uvicorn
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Path, Query

#import storage.sql.database

from test_orchestrator.storage import projects as projects_storage
from test_orchestrator.storage import configs as configs_storage
from test_orchestrator.storage import tars as tars_storage

from test_orchestrator.testing import commit as commit_testing
from test_orchestrator.testing import project as project_testing

from test_orchestrator.evaluation import reports

from test_orchestrator.storage.sql.database import init_db
Session = init_db()
app = FastAPI()


@app.put("/project/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: projects_storage.RegisterRequest):
    project_id = projects_storage.register(register_req)
    return {"project_id": project_id}


@app.delete("/project/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: int = Path(..., title="Id of the project to delete", gt=0)):
    if projects_storage.delete(project_id):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@app.put("/config/add/{project_id}", status_code=status.HTTP_200_OK)
async def add_project(project_id: int = Path(..., title="Id of the project to add config to", gt=0),
                      config: str = Body(...,
                                         description="Config as a string. Max length of 4096 characters.", max_length=65536)):
    config_id = configs_storage.store(project_id, config)
    return {"config_id": config_id}


@app.get("/config/get/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to get config from", gt=0),
                           config_id: int = Query(..., title="Id of the config to get", gt=0)):
    config = configs_storage.get(project_id, config_id)
    return {"config": config}


@app.get("/config/get_all/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    config_ids = configs_storage.get_all(project_id)
    return {"config_ids": config_ids}


@app.post("/test/commit/{project_id}", status_code=status.HTTP_200_OK)
async def request_commit_test(project_id: int = Path(..., title="Id of the project to test", gt=0),
                              commit: str = Query(...,
                                                  description="SHA1 Hash of the new commit to test. Tags or anything else are not accepted. Has to be a hexadecimal string of length 40.", min_length=40, max_length=40, regex=r"[0-9A-Fa-f]+")):
    test_id = commit.test(project_id, commit)
    return {"test_id": test_id}


@app.get("/test/commit/{project_id}", response_model=commit_testing.CommitTestReport, status_code=status.HTTP_200_OK)
async def read_commit_test_result(project_id: int = Path(..., title="Id of the tested project", gt=0),
                                  test_id: int = Query(..., title="Result id of the test", gt=0)):
    if not commit_testing.does_test_exist(project_id, test_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    elif not commit_testing.is_test_finished(project_id, test_id):
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                            detail="Test not ready")
    else:
        return commit_testing.get_test_report(project_id, test_id)


@app.post("/test/project/{project_id}", status_code=status.HTTP_200_OK)
async def request_project_test(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    test_id = project_testing.test(project_id)
    return {"test_id": test_id}


@app.get("/test/project/{project_id}")
async def read_project_test_status(project_id: int = Path(..., title="Id of the tested project", gt=0),
                                   test_id: int = Query(..., title="Result id of the test", gt=0)):
    if not project_testing.does_test_exist(project_id):
        raise HTTPException(status_code=404, detail="Item not found")
    elif not project_testing.is_test_finished(project_id):
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                            detail="Test not ready")
    else:
        return project_testing.get_test_report(project_id, test_id)


@app.get("/adapter")
async def get_adapter():
    return FileResponse("../static/performance-test-adapter")


@app.post("/reports/{identifier}", status_code=status.HTTP_200_OK)
async def request_project_test(report_id: str = Path(...,
                                                     description="Identifier of the report as string. Max length of 65536 characters.",
                                                     max_length=1000),
                               content: str = Body(...,
                                                   description="Content of the report as string. Max length of 65536 characters.",
                                                   max_length=65536)):
    reports.accept_report(report_id, content)
    return


@app.get("/tars/{tar_id}", status_code=status.HTTP_200_OK)
async def request_project_test(report_id: str = Path(...,
                                                     description="Identifier of the report as string. Max length of 65536 characters.",
                                                     max_length=1000)):
    tar_path = tars_storage.tar_id2tar_path(report_id)
    return FileResponse(tar_path)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("test_orchestrator.test_orchestrator:app",
                host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
