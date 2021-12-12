# APIRouter creates path operations for item module
from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import HTTPException
from fastapi.params import Path

from test_orchestrator import storage

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.put("/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: storage.RegisterRequest):
    project_id = storage.projects.register(register_req)
    return {"project_id": project_id}


@router.delete("/delete/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: int = Path(..., title="Id of the project to delete", gt=0)):
    if storage.projects.delete(project_id):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
