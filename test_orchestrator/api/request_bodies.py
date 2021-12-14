from typing import Optional
from pydantic import BaseModel, Field
from pydantic.networks import EmailStr, HttpUrl
from test_orchestrator.testing.selection.configs import SelectionStrategy


class TestRequest(BaseModel):
    n_commits: int = Field(..., description="n commits to test", gt=0),
    n_configs: int = Field(..., description="n configs to test", gt=0),
    first_commit_hash: str = Field(...,
                                   description="SHA1 Hash of the first commit to test.",
                                   min_length=40, max_length=40, regex=r"[0-9A-Fa-f]+"),
    last_commit_hash: str = Field(...,
                                  description="SHA1 Hash of the first commit to test.",
                                  min_length=40, max_length=40, regex=r"[0-9A-Fa-f]+"),
    selection_strategy: SelectionStrategy = Field(None,
                                                  description="Testing Strategy. See Enum for allowed values"),


class RegisterRequest(BaseModel):
    repo_url: HttpUrl = Field(...,
                              description="URL of the git repo of the project to test. Must be properly formatted URL including http(s)://")
    git_user: str = Field("git",
                          description="Git user of the repo. Max length of 32. Only \\w regex characters and \"-\" are allowed.", max_length=32, regex=r"(\w|-)+")
    auth_token: str = Field(...,
                            description="Auth token that allows pull access to the repository. Must consist be hexadecimal string of length 32.", min_length=32, max_length=32, regex=r"[0-9A-Fa-f]+")
    main_branch: str = Field("main",
                             description="Main Branch of the project. Assumed to be \"main\".  Only \\w regex characters and \"-\" are allowed.", max_length=32, regex=r"(\w|-)+")
    max_test_configs: int = Field(5,
                                  description="Number of configurations to test per run.", gt=0, le=10)
    name: str = Field(...,
                      description="Name of the project. Maximum of 256 characters", max_length=256)
    email: Optional[EmailStr] = Field(None,
                                      description="Email associated with the project")
    tester_command: str = Field(...,
                                description="Command that executes the specified tester.")
    tester_container: Optional[str] = Field(None,
                                            description="Optional additional testing container in case of two container setup.")
    two_container: bool = Field(False, description="Defines container setup.")
