import itertools
from typing import List

import storage
from sqlalchemy.orm import Session


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


def select(db: Session, project_id: int, n_configs: int) -> List[int]:
    test_ids = storage.projects.id2test_ids(db, project_id)
    # TODO Need to specify that this only always works against the current HEAD

    head_filepaths = storage.repos.get_filepaths(db, project_id, "HEAD")

    id_by_distance = {}
    for test_id in test_ids:
        commit_id = storage.tests.id2commit_id(db, test_ids)
        commit_hash = storage.commits.id2hash(db, commit_id)
        commit_filepaths = storage.repos.get_filepaths(
            db, project_id, commit_hash)
        distance = commit_distance(head_filepaths, commit_filepaths)
        id_by_distance[distance] = test_id

    sorted_by_distance = dict(sorted(id_by_distance.items()))

    top_tests = sorted_by_distance.values()[:n_configs]
    return [storage.tests.id2config_id(test) for test in top_tests]
