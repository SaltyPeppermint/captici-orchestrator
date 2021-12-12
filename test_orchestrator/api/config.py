# APIRouter creates path operations for item module
from fastapi import APIRouter, status
from fastapi.params import Path, Query, Body

from test_orchestrator import storage


router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


@router.put("/add/{project_id}", status_code=status.HTTP_200_OK)
async def add_project(project_id: int = Path(..., title="Id of the project to add config to", gt=0),
                      config: str = Body(...,
                                         description="Config as a string. Max length of 4096 characters.", max_length=65536)):
    config_id = storage.configs.store(project_id, config)
    return {"config_id": config_id}


@router.get("/get/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to get config from", gt=0),
                           config_id: int = Query(..., title="Id of the config to get", gt=0)):
    config = storage.configs.get(project_id, config_id)
    return {"config": config}


@router.get("/get_all/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(project_id: int = Path(..., title="Id of the project to test", gt=0)):
    config_ids = storage.configs.get_all(project_id)
    return {"config_ids": config_ids}
