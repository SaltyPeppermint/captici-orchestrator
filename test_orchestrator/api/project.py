# APIRouter creates path operations for item module
from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path

from .request_bodies import RegisterRequest
from test_orchestrator.storage import projects

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.put("/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: RegisterRequest):
    project_id = projects.register(register_req)
    return {"project_id": project_id}


@router.delete("/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
        project_id: int = Path(..., title="Id of the project to delete", gt=0)):

    if projects.delete(project_id):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
