from typing import List

import git
from sqlalchemy.orm import Session
from test_orchestrator.settings import config

from . import projects, commits


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
    repo.active_branch.name
    commits = []
    for commit in repo.iter_commits(rev=repo.active_branch.name):
        commits.append(commit)
    return [str(commit.hexsha) for commit in commits]


def get_filepaths(db: Session, project_id: int, commit_hash: str) -> List[str]:
    repo = git.Repo(get_repo_path(db, project_id))
    changed_files = repo.git.show(commit_hash, pretty="", name_only=True)
    # im essentiall coding against the cli but it works
    return changed_files.split("\n")


def is_parent_commit(
        db: Session,
        project_id: int,
        left_commit_id: str,
        right_commit_id: str) -> bool:

    left_commit_hash = commits.id2hash(left_commit_id)
    right_commit_hash = commits.id2hash(right_commit_id)

    repo = git.Repo(get_repo_path(db, project_id))
    right_commit = repo.commit(right_commit_hash)
    parent_hashes = [parent.hexsha for parent in right_commit.parents]
    return left_commit_hash in parent_hashes
