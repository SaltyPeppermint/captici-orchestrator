# APIRouter creates path operations for item module
from fastapi import APIRouter, status
from fastapi.params import Depends, Path, Query, Body
from sqlalchemy.orm import Session

from test_orchestrator.storage import configs
from test_orchestrator.storage.sql.database import get_db


router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


@router.put("/add/{project_id}", status_code=status.HTTP_200_OK)
async def add_project(
        project_id: int = Path(...,
                               title="Id of the project to add config to", gt=0),
        config: str = Body(...,
                           description="Config as a string. Max length of 4096 characters.", max_length=65536),
        db: Session = Depends(get_db)):

    config_id = configs.store(db, project_id, config)
    return {"config_id": config_id}


@router.get("/get/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(
        project_id: int = Path(...,
                               title="Id of the project to get config from", gt=0),
        config_id: int = Query(..., title="Id of the config to get", gt=0),
        db: Session = Depends(get_db)):

    config = configs.id2content(db, config_id)
    return {"config": config}


@router.get("/get_all/{project_id}", status_code=status.HTTP_200_OK)
async def register_project(
        project_id: int = Path(..., title="Id of the project to test", gt=0),
        db: Session = Depends(get_db)):

    config_ids = configs.project_id2ids(db, project_id)
    return {"config_ids": config_ids}
