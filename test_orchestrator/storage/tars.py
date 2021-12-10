
import pickle
import tarfile
import os
from typing import Iterable

from . import repositories
from . import projects
from test_orchestrator.settings import config


class TarInfo:
    def __init__(self, project_id: int, commit_hash: str):
        self.project_id = project_id
        self.commit_hash = commit_hash

    def serialize(self) -> str:
        return pickle.dumps(self).encode("base64", "strict")

    @classmethod
    def deserialize(cls, tar_id):
        return cls(pickle.loads(tar_id.decode("base64", "strict")))

    def __iter__(self) -> Iterable:
        yield self.project_id
        yield self.commit_hash


def get_tar_path(tar_folder, commit_hash) -> str:
    return f"{tar_folder}/{commit_hash}.tar.gz"


def get_tar_folder(project_id) -> str:
    nfs_mount = config["NFS"]["mount"]
    tar_dir = config["Directories"]["tar_dir"]
    return f"{nfs_mount}{tar_dir}/{project_id}-{projects.id2name(project_id)}"


def tar_id2tar_path(tar_id) -> str:
    project_id, commit_hash = TarInfo.deserialize(tar_id)
    tar_folder = get_tar_folder(project_id)
    return get_tar_path(tar_folder, commit_hash)


def tar_into(project_id: int, commit_hash: str) -> str:
    tar_folder = get_tar_folder(project_id)
    tar_path = get_tar_path(tar_folder, commit_hash)
    repo_path = repositories.get_repo_path(project_id)

    if not os.path.exists(repo_path):
        repo = repositories.clone_repo(project_id, repo_path)
    else:
        repo = repositories.update_repo(repo_path)

    main_branch = repo.active_branch.name
    repo.git.checkout(commit_hash)

    if not os.path.exists(tar_folder):
        os.makedirs(tar_folder)

    with tarfile.open(tar_path, mode="w:gz") as tar:
        tar.add(repo_path, recursive=True,
                filter=lambda tarinfo: None if ".git" in tarinfo.name else tarinfo)

    repo.git.checkout(main_branch)
    return TarInfo(project_id, commit_hash).serialize()
