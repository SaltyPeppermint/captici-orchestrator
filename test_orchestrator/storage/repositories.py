import git
import tarfile
import os
from . import projects


def get_git_cred(project_id: int):
    return ("github.com/BurntSushi/ripgrep.git", "git", "")


def clone_repo(project_id: int, repo_path: str):
    git_url, git_user, git_pw = get_git_cred(project_id)
    remote = f"https://{git_user}:{git_pw}@{git_url}"
    repo = git.Repo.clone_from(remote, repo_path)
    return repo


def update_repo(repo_path: str):
    repo = git.Repo(repo_path)
    repo.remotes.origin.pull()
    return repo


def get_tar_paths(project_id, commit_hash):
    tar_path = f"{os.getcwd()}/tars/{project_id}-{projects.id2name(project_id)}/{commit_hash}.tar.gz"
    tar_folder = f"{os.getcwd()}/tars/{project_id}-{projects.id2name(project_id)}"
    return tar_path, tar_folder


def tar_into(project_id: int, commit_hash: str):
    tar_path, tar_folder = get_tar_paths(project_id, commit_hash)
    repo_path = f"{os.getcwd()}/repos/{project_id}-{projects.id2name(project_id)}"

    if not os.path.exists(repo_path):
        repo = clone_repo(project_id, repo_path)
    else:
        repo = update_repo(repo_path)

    main_branch = repo.active_branch.name
    repo.git.checkout(commit_hash)

    if not os.path.exists(tar_folder):
        os.makedirs(tar_folder)

    with tarfile.open(tar_path, mode="w:gz") as tar:
        tar.add(repo_path, recursive=True,
                filter=lambda tarinfo: None if ".git" in tarinfo.name else tarinfo)

    repo.git.checkout(main_branch)
    return
