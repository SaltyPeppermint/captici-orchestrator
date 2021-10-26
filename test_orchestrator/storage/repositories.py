import git
import tarfile
import os


def get_git_cred(project_name: str):
    return ("https://example.com", "git", "password")


def clone_repo(project_name: str, repo_path: str):
    git_url, git_user, git_pw = get_git_cred(project_name)
    remote = f"https://{git_user}:{git_pw}@{git_url}"
    repo_path = f"/repos/{project_name}"
    repo = git.Repo.clone_from(remote, repo_path)
    return repo


def update_repo(repo_path: str):
    repo = git.Git(repo_path)
    repo.remotes.origin.pull()
    return repo


def tar_into(project_name: str, commit_hash: str):
    repo_path = f"/repos/{project_name}"
    if not os.path.exists(repo_path):
        repo = clone_repo(project_name, repo_path)
    else:
        repo = update_repo(repo_path)

    repo.git.checkout(commit_hash)
    tar_path = f"/tars/{project_name}/{commit_hash}.tar.gz"

    with tarfile.open(tar_path, mode="w:gz") as tar:
        tar.add(repo_path, recursive=True,
                filter=lambda tarinfo: None if ".git" in tarinfo.name else tarinfo)
