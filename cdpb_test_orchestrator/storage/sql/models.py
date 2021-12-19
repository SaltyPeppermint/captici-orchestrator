from cdpb_test_orchestrator import data_objects
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
    parser = Column(String(256), nullable=False)
    repo_url = Column(String(256), nullable=False)
    git_user = Column(String(256), nullable=False)
    auth_token = Column(String(256), nullable=False)
    main_branch = Column(String(256), nullable=False)
    config_path = Column(String(256), nullable=False)
    two_container = Column(Boolean(), nullable=False)
    tester_image = Column(String(256))
    email = Column(String(256))

    def __init__(self, project: data_objects.Project):
        self.name = project.name
        self.tester_command = project.tester_command
        self.result_path = project.result_path
        self.parser = project.parser.value
        self.repo_url = project.repo_url
        self.git_user = project.git_user
        self.auth_token = project.auth_token
        self.main_branch = project.main_branch
        self.config_path = project.config_path
        self.two_container = project.two_container
        self.tester_image = project.tester_image
        self.email = project.email

    def __repr__(self):
        return (
            f"<Project(id='{self.id}', name='{self.name}',"
            f" tester_command='{self.tester_command}',"
            f" result_path='{self.result_path}', parser_int='{self.parser_str}',"
            f" repo_url='{self.repo_url}', git_user='{self.git_user}',"
            f" main_branch='{self.main_branch}', auth_token='{self.auth_token}',"
            f" config_path='{self.config_path}'', two_container='{self.two_container}',"
            f" tester_image='{self.tester_image}', email='{self.email}')>"
        )


class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(String(65536), nullable=False)

    def __init__(self, project_id: int, content: str):
        self.project_id = project_id
        self.content = content

    def __repr__(self):
        return (
            f"<Config(id='{self.id}', project_id='{self.project_id}',"
            f" content='{self.content}')>"
        )


class TestGroup(Base):
    __tablename__ = "cdpb_test_groups"
    id = Column(Integer, Sequence("cdpb_test_groups_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    threshold = Column(Float, nullable=False)
    whole_project_test = Column(Boolean(), nullable=False)

    def __init__(self, project_id: int, threshold: float, whole_project_test: bool):
        self.project_id = project_id
        self.threshold = threshold
        self.whole_project_test = whole_project_test

    def __repr__(self):
        return f"<CDPB Test Group(id='{self.id}', project_id='{self.project_id}')>"


class CDPBTest(Base):
    __tablename__ = "cdpb_tests"
    id = Column(Integer, Sequence("cdpb_tests_id_seq"), primary_key=True)
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
        preceding_test_id: int | None,
        following_test_id: int | None,
    ):
        self.project_id = project_id
        self.config_id = config_id
        self.commit_hash = commit_hash
        self.result = None
        self.finished = False
        self.preceding_test_id = preceding_test_id
        self.following_test_id = following_test_id

    def __repr__(self):
        return (
            f"<CDPB Test(id='{self.id}', config_id='{self.config_id}',"
            f" commit_hash='{self.commit_hash}', content='{self.result}',"
            f" finished='{self.finished}'',"
            f" preceding_test_id='{self.preceding_test_id}'',"
            f" following_test_id='{self.following_test_id}')>"
        )


class TestInTestGroup(Base):
    __tablename__ = "cdpb_test_in_group"
    test_group_id = Column(Integer, ForeignKey("cdpb_test_groups.id"), primary_key=True)
    test_id = Column(Integer, ForeignKey("cdpb_tests.id"), primary_key=True)

    def __init__(self, test_group_id: int, test_id: int):
        self.test_group_id = test_group_id
        self.test_id = test_id

    def __repr__(self):
        return f"<test_group_id(id='{self.test_group_id}', test_id='{self.test_id}'>"
