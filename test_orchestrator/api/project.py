from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi.params import Depends, Path
from sqlalchemy.orm import Session

from test_orchestrator.storage import projects
from test_orchestrator.storage.sql.database import get_db
from .request_bodies import RegisterRequest

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.put("/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: RegisterRequest, db: Session = Depends(get_db)):
    project_id = projects.add(db, register_req)
    return {"project_id": project_id}


@router.delete("/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
        project_id: int = Path(..., title="Id of the project to delete", gt=0), db: Session = Depends(get_db)):

    if projects.delete(db, project_id):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
