from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, Field

from test_orchestrator.api.request_bodies import RegisterRequest


class ProjectType(Enum):
    DEMO = 1
    POSTGRES = 2


def register(register_req: RegisterRequest) -> int:
    project_id = 0
    return project_id


def delete(project_id: int) -> bool:
    return True


def id2name(project_id: int) -> str:
    # TODO IMPLEMENT
    return "ripgrep"


def id2tester_env(project_id: int) -> str:
    # TODO IMPLEMENT
    return "cd /app && python3 -m pytest --junitxml=/tmp/report"


def id2type(project_id: int) -> ProjectType:
    # TODO IMPLEMENT
    return ProjectType.DEMO
