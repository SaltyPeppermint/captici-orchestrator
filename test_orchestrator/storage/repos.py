from typing import List

import git
from sqlalchemy.orm import Session
from test_orchestrator.settings import config

from . import projects


def clone_repo(db: Session, project_id: int, repo_path: str) -> git.Repo:
    git_url, git_user, git_pw = projects.id2git_info(db, project_id)
    remote = f"https://{git_user}:{git_pw}@{git_url}"
    repo = git.Repo.clone_from(remote, repo_path)
    return repo


def update_repo(repo_path: str) -> git.Repo:
    repo = git.Repo(repo_path)
    repo.remotes.origin.pull()
    return repo


def get_repo_path(db: Session, project_id: int) -> str:
    nfs_mount = config["NFS"]["mount"]
    repos_dir = config["Directories"]["repos_dir"]
    project_name = projects.id2name(db, project_id)
    return f"{nfs_mount}{repos_dir}/{project_id}-{project_name}"


def get_all_commits(db: Session, project_id: int) -> List[str]:
    repo = git.Repo(get_repo_path(db, project_id))
    main_branch = repo.active_branch.name
    commits = []
    for commit in repo.iter_commits(rev=main_branch):
        commits.append(commit)
    return [str(commit.hexsha) for commit in commits]


def get_filepaths(db: Session, project_id: int, commit_hash: str) -> List[str]:
    repo = git.Repo(get_repo_path(db, project_id))
    changed_files = repo.git.show(commit_hash, pretty="", name_only=True)
    # im essentially coding against the cli but it works
    return changed_files.split("\n")


def is_parent_commit(
    db: Session, project_id: int, preceding_commit_hash: str, following_commit_hash: str
) -> bool:

    repo = git.Repo(get_repo_path(db, project_id))
    right_commit = repo.commit(following_commit_hash)
    parent_hashes = [parent.hexsha for parent in right_commit.parents]
    return preceding_commit_hash in parent_hashes
