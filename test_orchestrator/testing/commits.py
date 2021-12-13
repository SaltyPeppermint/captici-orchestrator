import math
from typing import List

from sqlalchemy.orm import Session
from test_orchestrator.storage import repositories

from test_orchestrator.testing.test import SelectionStrategy


def str2strategy(strategy_as_string: str) -> SelectionStrategy:
    if(strategy_as_string) == "all":
        return SelectionStrategy.ALL
    if(strategy_as_string) == "path_distance":
        return SelectionStrategy.PATH_DISTANCE


def commits_between(
        all_commit_hashs: List[str], first_commit_hash: str, last_commit_hash: str) -> List[str]:
    ix = iy = 0
    for i, v in enumerate(all_commit_hashs):
        if v == first_commit_hash:
            ix = i
        if v == last_commit_hash:
            iy = i
            break

    return all_commit_hashs[ix:iy]


def uniform_select(commit_hashs: List[str], n_commits: int) -> List[str]:
    if n_commits >= len(commit_hashs):
        return commit_hashs
    else:
        # len = 15, n_commits = 4: floor(15/4) = floor(3.75) = 3
        stepsize = math.floor(len(commit_hashs)/n_commits)
        # for len = 10 and n = 3: [0, 0+3=3, 3+3=6, 6+3=9] = [0,3,6,9]
        return commit_hashs[::stepsize]


def select_commits(
        db: Session, project_id: int, first_commit_hash: str, last_commit_hash: str, n_commits: int) -> List[str]:
    all_commit_hashs = repositories.get_all_commits(db, project_id)
    commits_hashs_in_range = commits_between(
        all_commit_hashs, first_commit_hash, last_commit_hash)
    return uniform_select(commits_hashs_in_range, n_commits)
