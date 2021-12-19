# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
import sqlalchemy
from cdpb_test_orchestrator.data_objects import Project
from cdpb_test_orchestrator.storage import projects
from cdpb_test_orchestrator.storage.sql.database import get_db
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_project(register_req: Project, db: Session = Depends(get_db)):
    register_req.id = None
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