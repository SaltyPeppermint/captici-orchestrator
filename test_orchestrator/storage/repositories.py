from typing import List, Tuple
import git

from . import projects
from test_orchestrator.settings import config


def get_git_cred(project_id: int) -> Tuple[str, str, str]:
    return ("github.com/BurntSushi/ripgrep.git", "git", "")


def clone_repo(project_id: int, repo_path: str) -> git.Repo:
    git_url, git_user, git_pw = get_git_cred(project_id)
    remote = f"https://{git_user}:{git_pw}@{git_url}"
    repo = git.Repo.clone_from(remote, repo_path)
    return repo


def update_repo(repo_path: str) -> git.Repo:
    repo = git.Repo(repo_path)
    repo.remotes.origin.pull()
    return repo


def get_repo_path(project_id) -> str:
    nfs_mount = config["NFS"]["mount"]
    repos_dir = config["Directories"]["repos_dir"]
    return f"{nfs_mount}{repos_dir}/{project_id}-{projects.id2name(project_id)}"


def get_all_commits(project_id) -> List[str]:
    # TODO IMPLEMENT
    return ["asdf", "asdfasdfasdf"]


def get_filepaths_in_commit(commit) -> List[str]:
    # TODO IMPLEMENT
    return ["/as", "/bla/blub"]
