from os import register_at_fork
from sqlalchemy import Sequence, Column, Boolean, Integer, String, ForeignKey
from sqlalchemy import Sequence, Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from test_orchestrator.api.request_bodies import RegisterRequest
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True)
    name = Column(String(256), nullable=False)
    tester_command = Column(String(256), nullable=False)
    repo_url = Column(String(256), nullable=False)
    git_user = Column(String(256), nullable=False)
    main_branch = Column(String(256), nullable=False)
    auth_token = Column(String(256), nullable=False)
    two_container = Column(Boolean(), nullable=False)
    tester_container = Column(String(256))
    email = Column(String(256))

    def __init__(self, register_req: RegisterRequest):
        self.repo_url = register_req.repo_url
        self.git_user = register_req.git_user
        self.auth_token = register_req.auth_token
        self.main_branch = register_req.main_branch
        self.name = register_req.name
        self.email = register_req.email
        self.tester_command = register_req.tester_command
        self.tester_container = register_req.tester_container
        self.two_container = register_req.two_container

    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}', tester_command='{self.tester_command}', repo_url='{self.repo_url}', git_user='{self.git_user}', main_branch='{self.main_branch}', auth_token='{self.auth_token}', two_container='{self.two_container}', tester_container='{self.tester_container}', email='{self.email}')>"


class Commit(Base):
    __tablename__ = "commits"
    id = Column(Integer, Sequence("commit_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    hash = Column(String(32), nullable=False)

    def __init__(self, project_id, hash, tested):
        self.project_id = project_id
        self.hash = hash

    def __repr__(self):
        return f"<Commit(id='{self.id}', project_id='{self.project_id}', hash='{self.hash}')>"


class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(String(65536), nullable=False)

    def __init__(self, project_id, content):
        self.project_id = project_id
        self.content = content

    def __repr__(self):
        return f"<Config(id='{self.id}', project_id='{self.project_id}', content='{self.content}')>"


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, Sequence("test_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    def __init__(self, project_id):
        self.project_id = project_id

    def __repr__(self):
        return f"<Test(id='{self.id}', project_id='{self.project_id}')>"


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, Sequence("result_id_seq"), primary_key=True)
    config_id = Column(Integer, ForeignKey("configs.id"), nullable=False)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False)
    content = Column(String(65536))
    finished = Column(Boolean(False), nullable=False)

    def __init__(self, config_id, commit_id):
        self.config_id = config_id
        self.commit_id = commit_id
        self.content = ""
        self.finished = False

    def __repr__(self):
        return f"<Result(id='{self.id}', config_id='{self.config_id}', commit_id='{self.commit_id}', content='{self.content}', finished='{self.finished}')>"


class ResultsInTest(Base):
    __tablename__ = 'results_in_tests'
    test_id = Column(Integer, ForeignKey("tests.id"), primary_key=True)
    result_id = Column(Integer, ForeignKey("results.id"), primary_key=True)

    def __init__(self, test_id, result_id):
        self.test_id = test_id
        self.result_id = result_id

    def __repr__(self):
        return f"<test_id(id='{self.test_id}', result_id='{self.result_id}'>"
