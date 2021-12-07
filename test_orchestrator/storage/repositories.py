import git

from storage import projects
from settings import REPOS_DIR, NFS_MOUNT


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


def get_repo_path(project_id):
    return f"{NFS_MOUNT}{REPOS_DIR}/{project_id}-{projects.id2name(project_id)}"
