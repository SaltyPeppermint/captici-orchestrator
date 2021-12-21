# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
from cdpb_test_orchestrator.data_objects import Project
from cdpb_test_orchestrator.storage import projects
from cdpb_test_orchestrator.storage.sql.database import get_db
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Query
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", status_code=status.HTTP_200_OK)
def add_project(project_to_add: Project, db: Session = Depends(get_db)):
    project_to_add.id = None
    project_id = projects.add(db, project_to_add)
    return {"project_id": project_id}


@router.get("/get", status_code=status.HTTP_200_OK)
def get_project(
    project_id: int = Query(..., title="Id of the project to get", gt=0),
    db: Session = Depends(get_db),
):
    try:
        project = projects.id2project(db, project_id)
        return project
    except NoResultFound as no_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from no_result


@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int = Query(..., title="Id of the project to delete", gt=0),
    db: Session = Depends(get_db),
):
    try:
        projects.deleteById(db, project_id)
        return
    except NoResultFound as no_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from no_result
