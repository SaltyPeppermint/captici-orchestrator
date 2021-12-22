from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.networks import EmailStr, HttpUrl


class SelectionStrategy(str, Enum):
    PATH_DISTANCE = "path_distance"


class ResultParser(str, Enum):
    JUNIT = "junit"


class CommitTestRequest(BaseModel):
    project_id: int = Field(..., description="Id of the Project to test.", gt=0)
    n_commits: int = Field(..., description="n commits to test", gt=0)
    n_configs: int = Field(..., description="n configs to test", gt=0)
    commit_hash: str = Field(
        ...,
        description="SHA1 Hash of the first commit to test.",
        min_length=40,
        max_length=40,
        regex=r"[0-9A-Fa-f]+",
    )
    threshold: float = Field(0.25, description="Threshold for detection.")
    selection_strategy: SelectionStrategy = Field(
        ..., description="Testing Strategy. See Enum for allowed values."
    )


class ProjectTestRequest(BaseModel):
    project_id: int = Field(..., description="Id of the Project to test.", gt=0)
    n_commits: int = Field(..., description="n commits to test", gt=0)
    threshold: float = Field(
        0.25, description="Threshold for regression detection per test_group."
    )
    # n_configs: int = Field(..., description="n configs to test", gt=0),


class Project(BaseModel):
    id: int = Field(
        None, description="Id of the orm object. Will be nulled regardless."
    )
    name: str = Field(
        ...,
        description="Name of the project. Maximum of 256 characters",
        max_length=256,
    )
    tester_command: str = Field(
        ..., description="Command that executes the specified tester."
    )
    result_path: str = Field(
        ..., description="Path where the report will be generated to upload."
    )
    parser: ResultParser = Field(
        ..., description="Parser used to parse the report by the test."
    )
    repo_url: HttpUrl = Field(
        ...,
        description=(
            "URL of the git repo of the project to test. Must be properly formatted URL"
            " WITH http(s)://"
        ),
    )
    git_user: str = Field(
        "git",
        description=(
            "Git user of the repo. Max length of 32. Only \\w regex characters and '-'"
            " are allowed."
        ),
        max_length=32,
        regex=r"(\w|-)+",
    )
    auth_token: str = Field(
        ...,
        description=(
            "Auth token that allows pull access to the repository. Must consist be"
            " hexadecimal string with minlength 8 and maxlength 32."
        ),
        min_length=8,
        max_length=32,
        regex=r"[0-9A-Za-z]+",
    )
    main_branch: str = Field(
        "main",
        description=(
            "Main Branch of the project. Assumed to be main. Only \\w regex characters"
            " and are allowed."
        ),
        max_length=32,
        regex=r"(\w|-)+",
    )
    dockerfile_path: str = Field(
        ...,
        description="Path where the report will be generated to upload.",
    )
    config_path: str = Field(
        ..., description="Mount point of the configuration file. Use Unix Path."
    )
    two_container: bool = Field(False, description="Defines container setup.")
    tester_image: Optional[str] = Field(
        None, description="Optional additional testing container."
    )
    email: Optional[EmailStr] = Field(
        None, description="Email associated with the project"
    )

    class Config:
        orm_mode = True


class TestResponse(BaseModel):
    individual_results: Dict[int, Optional[float]]
    is_regression: bool
    regressing_config: Optional[List[int]] = None


class Test(BaseModel):
    id: int
    result: str
    commit_hash: str
    config_id: int
    config_content: str
    project: Project
