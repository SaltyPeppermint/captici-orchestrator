from typing import List, Tuple
import git
from sqlalchemy.orm import Session

from . import projects
from test_orchestrator.settings import config


def get_git_cred(db: Session, project_id: int) -> Tuple[str, str, str]:
    return ("github.com/BurntSushi/ripgrep.git", "git", "")


def clone_repo(db: Session, project_id: int, repo_path: str) -> git.Repo:
    git_url, git_user, git_pw = get_git_cred(db, project_id)
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
    return f"{nfs_mount}{repos_dir}/{project_id}-{projects.id2name(db, project_id)}"


def get_all_commits(db: Session, project_id: int) -> List[str]:
    repo = git.Repo(get_repo_path(db, project_id))
    repo.active_branch.name
    commits = []
    for commit in repo.iter_commits(rev=repo.active_branch.name):
        commits.append(commit)
    return [str(commit.hexsha) for commit in commits]


def get_filepaths_in_commit(
        db: Session, project_id: int, commit_hash: str) -> List[str]:

    repo = git.Repo(get_repo_path(db, project_id))
    changed_files = repo.git.show(commit_hash, pretty="", name_only=True)
    # im essentiall coding against the cli but it works
    return changed_files.split("\n")
