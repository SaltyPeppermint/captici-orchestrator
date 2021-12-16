import itertools
from typing import List, Tuple

from sqlalchemy.orm import Session
from test_orchestrator import storage


def common_prefix_len(arr1: List[str], arr2: List[str]) -> int:
    i = 0
    while i < len(arr1) and i < len(arr2):
        if arr1[i] != arr2[i]:
            break
        i += 1

    return i


def file_path_distance(path1: str, path2: str) -> int:
    arr1 = path1.split("/")
    arr2 = path2.split("/")
    return len(arr1) + len(arr2) - 2 * common_prefix_len(arr1, arr2)


def commit_distance(
        commit_files1: List[str], commit_files2: List[str]) -> float:

    path_product = itertools.product(commit_files1, commit_files2)
    path_distances = itertools.starmap(path_product)
    return sum(path_distances) / len(path_distances)


def select(db: Session, project_id: int, n_configs: int) -> List[Tuple[str, int]]:
    test_ids = storage.tests.project_id2ids(db, project_id)
    # TODO Need to specify that this only always works against the current HEAD

    head_filepaths = storage.repos.get_filepaths(db, project_id, "HEAD")

    by_distance = {}
    for test_id in test_ids:
        commit_hash = storage.tests.id2commit_hash(db, test_ids)
        commit_filepaths = storage.repos.get_filepaths(
            db, project_id, commit_hash)
        distance = commit_distance(head_filepaths, commit_filepaths)
        by_distance[distance] = test_id

    sorted_by_distance = dict(sorted(by_distance.items()))

    top_tests = sorted_by_distance.values()[:n_configs]
    return top_tests
