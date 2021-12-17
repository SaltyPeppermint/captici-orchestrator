# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
# APIRouter creates path operations for item module
from fastapi import APIRouter, status
from fastapi.params import Body, Depends, Query
from sqlalchemy.orm import Session
from test_orchestrator import storage
from test_orchestrator.storage.sql.database import get_db

router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", status_code=status.HTTP_200_OK)
async def add_project(
    project_id: int = Query(..., title="Id of the project to add config", gt=0),
    config: str = Body(
        ..., description="Config as a str. Max length 4096.", max_length=65536
    ),
    db: Session = Depends(get_db),
):
    config_id = storage.configs.add(db, project_id, config)
    return {"config_id": config_id}


@router.get("/get", status_code=status.HTTP_200_OK)
async def get_config_content(
    config_id: int = Query(..., title="Id of the config to get", gt=0),
    db: Session = Depends(get_db),
):
    config = storage.configs.id2content(db, config_id)
    return {"config": config}


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def register_project(
    project_id: int = Query(..., title="Id of the project to test", gt=0),
    db: Session = Depends(get_db),
):
    config_ids = storage.configs.project_id2ids(db, project_id)
    return {"config_ids": config_ids}
