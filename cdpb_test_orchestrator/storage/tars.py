import os
import tarfile

from cdpb_test_orchestrator import settings
from cdpb_test_orchestrator.data_objects import Project

from . import repos


def get_tar_path(tar_folder, commit_hash) -> str:
    return f"{tar_folder}/{commit_hash}.tar.gz"


def get_tar_folder(project_name: str, project_id: int) -> str:
    tars_dir = settings.tars_dir
    return f"{tars_dir}/{project_id}-{project_name}"


def tar_into(
    project: Project,
    commit_hash: str,
) -> str:
    tar_folder = get_tar_folder(project.name, project.id)
    tar_path = get_tar_path(tar_folder, commit_hash)

    repo = repos.get_repo(project)

    main_branch = repo.active_branch.name
    repo.git.checkout(commit_hash)

    if not os.path.exists(tar_folder):
        os.makedirs(tar_folder)

    with tarfile.open(tar_path, mode="w:gz") as tar:
        tar.add(
            repos.get_repo_path(project.name, project.id),
            arcname="",
            filter=lambda tarinfo: None if ".git" in tarinfo.name else tarinfo,
        )
    repo.git.checkout(main_branch)
    return tar_path
