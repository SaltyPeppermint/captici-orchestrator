from sqlalchemy import Boolean, Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, Sequence("project_id_seq"), primary_key=True)
    name = Column(String(256), nullable=False)
    tester_command = Column(String(256), nullable=False)
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
            repo_url: str,
            git_user: str,
            auth_token: str,
            main_branch: str,
            config_path: str,
            two_container: bool,
            tester_image: str,
            email: str):

        self.name = name
        self.tester_command = tester_command
        self.repo_url = repo_url
        self.git_user = git_user
        self.auth_token = auth_token
        self.main_branch = main_branch
        self.config_path = config_path
        self.two_container = two_container
        self.tester_image = tester_image
        self.email = email

    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}', tester_command='{self.tester_command}', repo_url='{self.repo_url}', git_user='{self.git_user}', main_branch='{self.main_branch}', auth_token='{self.auth_token}', config_path='{self.config_path}'', two_container='{self.two_container}', tester_image='{self.tester_image}', email='{self.email}')>"


class Commit(Base):
    __tablename__ = "commits"
    id = Column(Integer, Sequence("commit_id_seq"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    commit_hash = Column(String(32), nullable=False)

    def __init__(self, project_id: int, commit_hash: str):
        self.project_id = project_id
        self.commit_hash = commit_hash

    def __repr__(self):
        return f"<Commit(id='{self.id}', project_id='{self.project_id}', commit_hash='{self.commit_hash}')>"


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
    whole_project_test = Column(Boolean(), nullable=False)

    def __init__(self, project_id: int, whole_project_test: bool):
        self.project_id = project_id
        self.whole_project_test = whole_project_test

    def __repr__(self):
        return f"<Test Group(id='{self.id}', project_id='{self.project_id}')>"


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, Sequence("tests_id_seq"), primary_key=True)
    config_id = Column(Integer, ForeignKey("configs.id"), nullable=False)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False)
    preceding_test_id = Column(Integer, ForeignKey("commits.id"))
    following_commit_id = Column(Integer, ForeignKey("commits.id"))
    result = Column(String(65536))
    finished = Column(Boolean(False), nullable=False)
    revelead_cdpb = Column(Boolean(False), nullable=False)

    def __init__(
            self,
            config_id: int,
            commit_id: int,
            preceding_commit_id: int | None,
            following_commit_id: int | None):

        self.config_id = config_id
        self.commit_id = commit_id
        self.result = None
        self.finished = False
        self.revealed_bug = False
        self.preceding_commit_id = preceding_commit_id
        self.following_commit_id = following_commit_id

    def __repr__(self):
        return f"<Test(id='{self.id}', config_id='{self.config_id}', commit_id='{self.commit_id}', content='{self.result}', finished='{self.finished}'', preceding_commit_id='{self.preceding_commit_id}'', following_commit_id='{self.following_commit_id}')>"


class TestInTestGroup(Base):
    __tablename__ = 'test_in_test_group'
    test_group_id = Column(Integer, ForeignKey(
        "test_groups.id"), primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"), primary_key=True)

    def __init__(self, test_group_id: int, test_id: int):
        self.test_group_id = test_group_id
        self.test_id = test_id

    def __repr__(self):
        return f"<test_group_id(id='{self.test_group_id}', test_id='{self.test_id}'>"
