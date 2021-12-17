from typing import Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Float

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True)
    name = Column(String(256), nullable=False)
    tester_command = Column(String(256), nullable=False)
    result_path = Column(String(256), nullable=False)
    parser_str = Column(String(256), nullable=False)
    repo_url = Column(String(256), nullable=False)
    git_user = Column(String(256), nullable=False)
    auth_token = Column(String(256), nullable=False)
    main_branch = Column(String(256), nullable=False)
    config_path = Column(String(256), nullable=False)
    two_container = Column(Boolean(), nullable=False)
    tester_image = Column(String(256))
    email = Column(String(256))

    def __init__(
        self,
        name: str,
        tester_command: str,
        result_path: str,
        parser_str: str,
        repo_url: str,
        git_user: str,
        auth_token: str,
        main_branch: str,
        config_path: str,
        two_container: bool,
        tester_image: Optional[str],
        email: Optional[str],
    ):

        self.name = name
        self.tester_command = tester_command
        self.result_path = result_path
        self.parser_str = parser_str
        self.repo_url = repo_url
        self.git_user = git_user
        self.auth_token = auth_token
        self.main_branch = main_branch
        self.config_path = config_path
        self.two_container = two_container
        self.tester_image = tester_image
        self.email = email

    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}', tester_command='{self.tester_command}', result_path='{self.result_path}', parser_int='{self.parser_str}', repo_url='{self.repo_url}', git_user='{self.git_user}', main_branch='{self.main_branch}', auth_token='{self.auth_token}', config_path='{self.config_path}'', two_container='{self.two_container}', tester_image='{self.tester_image}', email='{self.email}')>"


class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(String(65536), nullable=False)

    def __init__(self, project_id: int, content: str):
        self.project_id = project_id
        self.content = content

    def __repr__(self):
        return f"<Config(id='{self.id}', project_id='{self.project_id}', content='{self.content}')>"


class TestGroup(Base):
    __tablename__ = "test_groups"
    id = Column(Integer, Sequence("test_groups_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    threshold = Column(Float, nullable=False)
    whole_project_test = Column(Boolean(), nullable=False)

    def __init__(self, project_id: int, threshold: float, whole_project_test: bool):

        self.project_id = project_id
        self.threshold = threshold
        self.whole_project_test = whole_project_test

    def __repr__(self):
        return f"<Test Group(id='{self.id}', project_id='{self.project_id}')>"


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, Sequence("tests_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    config_id = Column(Integer, ForeignKey("configs.id"), nullable=False)
    commit_hash = Column(String(32), nullable=False)
    preceding_test_id = Column(Integer)
    following_test_id = Column(Integer)
    result = Column(String(65536))
    finished = Column(Boolean(False), nullable=False)

    def __init__(
        self,
        project_id: int,
        config_id: int,
        commit_hash: str,
        preceding_test_id: Optional[int],
        following_test_id: Optional[int],
    ):

        self.project_id = project_id
        self.config_id = config_id
        self.commit_hash = commit_hash
        self.result = None
        self.finished = False
        self.preceding_test_id = preceding_test_id
        self.following_test_id = following_test_id

    def __repr__(self):
        return f"<Test(id='{self.id}', config_id='{self.config_id}', commit_hash='{self.commit_hash}', content='{self.result}', finished='{self.finished}'', preceding_test_id='{self.preceding_test_id}'', following_test_id='{self.following_test_id}')>"


class TestInTestGroup(Base):
    __tablename__ = "test_in_test_group"
    test_group_id = Column(Integer, ForeignKey("test_groups.id"), primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"), primary_key=True)

    def __init__(self, test_group_id: int, test_id: int):
        self.test_group_id = test_group_id
        self.test_id = test_id

    def __repr__(self):
        return f"<test_group_id(id='{self.test_group_id}', test_id='{self.test_id}'>"
