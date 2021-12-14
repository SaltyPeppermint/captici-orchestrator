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


def select(db: Session, project_id: int, n_configs: int) -> List[int]:
    result_ids = storage.projects.id2result_ids(db, project_id)
    # TODO Need to specify that this only always works against the current HEAD

    head_filepaths = storage.repositories.get_filepaths_in_commit(
        db, project_id, "HEAD")

    id_by_distance = {}
    for result_id in result_ids:
        commit_id = storage.results.id2commit_id(db, result_ids)
        commit_hash = storage.commits.id2hash(db, commit_id)
        commit_filepaths = storage.repositories.get_filepaths_in_commit(
            db, project_id, commit_hash)
        distance = commit_distance(head_filepaths, commit_filepaths)
        id_by_distance[distance] = result_id

    sorted_by_distance = dict(sorted(id_by_distance.items()))

    top_results = sorted_by_distance.values()[:n_configs]
    return [storage.results.id2config_id(result) for result in top_results]
