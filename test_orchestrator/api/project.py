# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
import sqlalchemy
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Query
from sqlalchemy.orm import Session
from test_orchestrator.storage import projects
from test_orchestrator.storage.sql.database import get_db

from .request_bodies import RegisterRequest

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_project(
    register_req: RegisterRequest, db: Session = Depends(get_db)
):

    project_id = projects.add(db, register_req)
    return {"project_id": project_id}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int = Query(..., title="Id of the project to delete", gt=0),
    db: Session = Depends(get_db),
):

    try:
        projects.deleteById(db, project_id)
        return
    except sqlalchemy.exc.NoResultFound as no_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from no_result
