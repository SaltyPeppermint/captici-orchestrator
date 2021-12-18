import math
from typing import List

from cdpb_test_orchestrator.storage import repos
from sqlalchemy.orm import Session


def choose_middle(left_bounding_item, right_bounding_item, items):
    ix = iy = 0
    for i, v in enumerate(items):
        if v == left_bounding_item:
            ix = i
        if v == right_bounding_item:
            iy = i
            break

    items_in_window = items[ix:iy]
    middle_item = items_in_window[len(items_in_window) // 2]
    # // is division without remainder, perfect here

    return middle_item


def uniform_choice(commit_hashs: List[str], n_commits: int) -> List[str]:
    if n_commits >= len(commit_hashs):
        return commit_hashs
    else:
        # len = 15, n_commits = 4: floor(15/4) = floor(3.75) = 3
        stepsize = math.floor(len(commit_hashs) / n_commits)
        # for len = 10 and n = 3: [0, 0+3=3, 3+3=6, 6+3=9] = [0,3,6,9]
        return commit_hashs[::stepsize]


def middle_select(
    db: Session, project_id: int, preceding_commit_hash: str, following_commit_hash: str
) -> str:

    all_commit_hashs = repos.get_all_commits(db, project_id)
    middle_item = choose_middle(
        preceding_commit_hash, following_commit_hash, all_commit_hashs
    )
    return middle_item


def initial_sample_select(db: Session, project_id: int, n_commits: int) -> List[str]:

    all_commit_hashs = repos.get_all_commits(db, project_id)

    return uniform_choice(all_commit_hashs, n_commits)
