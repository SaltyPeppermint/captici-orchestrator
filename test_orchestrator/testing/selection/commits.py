import math
from typing import List

from sqlalchemy.orm import Session
from storage import repos


def uniform_choice(commit_hashs: List[str], n_commits: int) -> List[str]:
    if n_commits >= len(commit_hashs):
        return commit_hashs
    else:
        # len = 15, n_commits = 4: floor(15/4) = floor(3.75) = 3
        stepsize = math.floor(len(commit_hashs)/n_commits)
        # for len = 10 and n = 3: [0, 0+3=3, 3+3=6, 6+3=9] = [0,3,6,9]
        return commit_hashs[::stepsize]


def middle_select(
        db: Session,
        project_id: int,
        left_commit_hash: str,
        right_commit_hash: str) -> str:
    all_commit_hashs = repos.get_all_commits(db, project_id)
    ix = iy = 0
    for i, v in enumerate(all_commit_hashs):
        if v == left_commit_hash:
            ix = i
        if v == right_commit_hash:
            iy = i
            break

    commits_in_window = all_commit_hashs[ix:iy]
    # // is division without remainder, perfect here
    return commits_in_window[len(commits_in_window)//2]


def initial_sample_select(
        db: Session,
        project_id: int,
        n_commits: int) -> List[str]:

    all_commit_hashs = repos.get_all_commits(db, project_id)

    return uniform_choice(all_commit_hashs, n_commits)
