import itertools
from typing import Dict, List, Tuple

from cdpb_test_orchestrator import storage
from cdpb_test_orchestrator.data_objects import Project


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


def commit_distance(commit_files1: List[str], commit_files2: List[str]) -> float:

    path_product = itertools.product(commit_files1, commit_files2)
    path_distances = []
    for path1, path2 in path_product:
        path_distances.append(file_path_distance(path1, path2))
    return sum(path_distances) / len(path_distances)


def select(
    project: Project, n_configs: int, bug_dict: Dict[int, str]
) -> List[Tuple[float, int]]:

    # Need to specify that this only always works against the current HEAD
    head_filepaths = storage.repos.get_filepaths(project.name, project.id, "HEAD")

    by_distance = {}
    for test_id, commit_hash in bug_dict.items():
        commit_filepaths = storage.repos.get_filepaths(
            project.name, project.id, commit_hash
        )
        distance = commit_distance(head_filepaths, commit_filepaths)
        by_distance[distance] = test_id

    sorted_by_distance = dict(sorted(by_distance.items()))

    top_tests = list(sorted_by_distance.items())[:n_configs]
    return top_tests
