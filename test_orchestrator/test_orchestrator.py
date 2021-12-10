from starlette.responses import FileResponse
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.params import Body, Path, Query

from test_orchestrator import storage
from test_orchestrator import testing

app = FastAPI()


@app.put("/project/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: storage.RegisterRequest):
    project_id = storage.projects.register(register_req)
    return {"project_id": project_id}


@app.delete("/project/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: int = Path(..., title="Id of the project to delete", gt=0)):
    if storage.projects.delete(project_id):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@app.put("/config/add/{project_id}", status_code=status.HTTP_200_OK)
async def add_project(project_id: int = Path(..., title="Id of the project to add config to", gt=0),
                      config: str = Body(...,
                                         description="Config as a string. Max length of 4096 characters.", max_length=65536)):
    config_id = storage.configs.store(project_id, config)
    return {"config_id": config_id}


@app.get("/config/get/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to get config from", gt=0),
                           config_id: int = Query(..., title="Id of the config to get", gt=0)):
    config = storage.configs.get(project_id, config_id)
    return {"config": config}


@app.get("/config/get_all/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    config_ids = storage.configs.get_all(project_id)
    return {"config_ids": config_ids}


@app.post("/test/commit/{project_id}", status_code=status.HTTP_200_OK)
async def request_commit_test(project_id: int = Path(..., title="Id of the project to test", gt=0),
                              commit: str = Query(...,
                                                  description="SHA1 Hash of the new commit to test. Tags or anything else are not accepted. Has to be a hexadecimal string of length 40.", min_length=40, max_length=40, regex=r"[0-9A-Fa-f]+")):
    test_id = commit.test(project_id, commit)
    return {"test_id": test_id}


@app.get("/test/commit/{project_id}", response_model=storage.Report, status_code=status.HTTP_200_OK)
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


@app.post("/test/project/{project_id}", status_code=status.HTTP_200_OK)
async def request_project_test(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    test_id = testing.project.test(project_id)
    return {"test_id": test_id}


@app.get("/test/project/{project_id}")
async def read_project_test_status(project_id: int = Path(..., title="Id of the tested project", gt=0),
                                   test_id: int = Query(..., title="Result id of the test", gt=0)):
    if not testing.project.does_test_exist(project_id):
        raise HTTPException(status_code=404, detail="Item not found")
    elif not testing.project.is_test_finished(project_id):
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,
                            detail="Test not ready")
    else:
        return storage.reports.get_test_report(project_id, test_id)


@app.get("/adapter")
async def get_adapter():
    return FileResponse("../static/performance-test-adapter")


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
