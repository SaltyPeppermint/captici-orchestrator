import itertools
from typing import List, Tuple

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


def commit_distance(commit1: str, commit2: str) -> float:
    commit_files1 = storage.repositories.get_filepaths_in_commit(commit1)
    commit_files2 = storage.repositories.get_filepaths_in_commit(commit2)
    path_product = itertools.product(commit_files1, commit_files2)
    path_distances = itertools.starmap(path_product)
    return sum(path_distances) / len(path_distances)


def initial_select(project_id: int) -> Tuple[List[str], List[str]]:
    # TODO GIT GET INITAL SAMPLING OF COMMITS
    storage.repositories.get_all_commits
    commits_to_test = storage.repositories.get_all_commits(project_id)
    config_ids_to_test = storage.configs.get_all_ids(project_id)
    configs_to_test = []
    for config_id in config_ids_to_test:
        config = storage.configs.get_config_content(project_id, config_id)
        configs_to_test.append(config)
    return commits_to_test, configs_to_test
