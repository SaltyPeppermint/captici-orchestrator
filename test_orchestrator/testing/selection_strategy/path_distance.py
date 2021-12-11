import itertools
from typing import List


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
    path_distances = itertools.starmap(path_product)
    return sum(path_distances) / len(path_distances)
