import re
from typing import List

import git
from cdpb_test_orchestrator.settings import get_config


def auth_info2clone_url(repo_url: str, git_user: str, auth_token: str) -> str:
    if git_user == "git" and auth_token is None:
        return repo_url
    else:
        auth = f"{git_user}:{auth_token}"
        protocol, fqdn = re.split(r"://", repo_url, maxsplit=1)
        return f"{protocol}://{auth}@{fqdn}"


def clone_repo(clone_url: str, repo_path: str) -> git.Repo:
    repo = git.Repo.clone_from(clone_url, repo_path)
    return repo


def update_repo(repo_path: str) -> git.Repo:
    repo = git.Repo(repo_path)
    repo.remotes.origin.pull()
    return repo


def get_repo_path(project_name: str, project_id: int) -> str:
    config = get_config()
    nfs_mount = config["NFS"]["mount"]
    repos_dir = config["Directories"]["repos_dir"]
    return f"{nfs_mount}{repos_dir}/{project_id}-{project_name}"


def get_all_commits(project_name: str, project_id: int) -> List[str]:
    repo = git.Repo(get_repo_path(project_name, project_id))
    main_branch = repo.active_branch.name
    commits = []
    for commit in repo.iter_commits(rev=main_branch):
        commits.append(commit)
    return [str(commit.hexsha) for commit in commits]


def get_filepaths(project_name: str, project_id: int, commit_hash: str) -> List[str]:
    repo = git.Repo(get_repo_path(project_name, project_id))
    changed_files = repo.git.show(commit_hash, pretty="", name_only=True)
    # im essentially coding against the cli but it works
    return changed_files.split("\n")


def is_parent_commit(
    project_name: str,
    project_id: int,
    preceding_commit_hash: str,
    following_commit_hash: str,
) -> bool:
    repo = git.Repo(get_repo_path(project_name, project_id))
    right_commit = repo.commit(following_commit_hash)
    parent_hashes = [parent.hexsha for parent in right_commit.parents]
    return preceding_commit_hash in parent_hashes
