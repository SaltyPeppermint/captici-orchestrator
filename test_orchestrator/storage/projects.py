from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from enum import Enum


class ProjectType(Enum):
    DEMO = 1
    POSTGRES = 2


class RegisterRequest(BaseModel):
    repo_url: HttpUrl = Field(...,
                              description="URL of the git repo of the project to test. Must be properly formatted URL including http(s)://")
    git_user: str = Field(
        "git", description="Git user of the repo. Max length of 32. Only \\w regex characters and \"-\" are allowed.", max_length=32, regex=r"(\w|-)+")
    auth_token: str = Field(
        ..., description="Auth token that allows pull access to the repository. Must consist be hexadecimal string of length 32.", min_length=32, max_length=32, regex=r"[0-9A-Fa-f]+")
    main_branch: str = Field(
        "main", description="Main Branch of the project. Assumed to be \"main\".  Only \\w regex characters and \"-\" are allowed.", max_length=32, regex=r"(\w|-)+")
    max_test_configs: int = Field(
        5, description="Number of configurations to test per run.", gt=0, le=10)
    project_name: Optional[str] = Field(None,
                                        description="Name of the project. Maximum of 256 characters", max_length=256)
    email: Optional[EmailStr] = Field(None,
                                      description="Email associated with the project")


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
