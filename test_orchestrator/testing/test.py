from typing import List, Tuple

import k8s
import storage
from api.request_bodies import CommitTestRequest, ProjectTestRequest
from sqlalchemy.orm import Session

from .selection.commits import initial_sample_select, middle_select
from .selection.configs import select_configs


def test_single_commit(
        db: Session,
        project_id: int,
        req: CommitTestRequest) -> int:
    test_id = storage.tests.add(db, project_id, False)

    config_ids_to_test = select_configs(
        db, project_id, req.n_configs, req.selection_strategy)
    test_commit(db, project_id, test_id, req.commit_hash, config_ids_to_test)
    return test_id


def test_whole_project(
        db: Session,
        project_id: int,
        req: ProjectTestRequest) -> int:
    test_id = storage.tests.add(db, project_id, True)

    commit_hashs = initial_sample_select(
        db, project_id, req.n_commits)
    config_ids_to_test = storage.projects.id2config_ids(db, project_id)
    i = len(commit_hashs)
    for i in range(0, len(commit_hashs)):
        previous_commit_id, following_commit_id = assign_commit_boundaries(
            db, project_id, commit_hashs, i)
        test_commit(
            db, project_id, test_id, commit_hashs[i],            config_ids_to_test, previous_commit_id, following_commit_id)
    return test_id


def assign_commit_boundaries(
        db: Session,
        project_id: int,
        commit_hashs: List[str],
        i: int) -> Tuple[int, int]:

    if i == 0:
        previous_commit_id = None
    else:
        previous_commit_id = storage.commits.add_or_get(
            db, project_id, commit_hashs[i-1])

    if i == len(commit_hashs) - 1:
        following_commit_id = None
    else:
        following_commit_id = storage.commits.add_or_get(
            db, project_id, commit_hashs[i+1])

    return previous_commit_id, following_commit_id


def binary_search_testing(
        db: Session,
        project_id: int,
        left_result_id: str,
        right_result_id: str,
        config_id: int,
        test_id: int) -> int:

    left_commit_id = storage.results.id2commit_id(left_result_id)
    right_commit_id = storage.results.id2commit_id(right_result_id)

    left_hash = storage.commits.id2hash(left_commit_id)
    right_hash = storage.commits.id2hash(right_commit_id)

    is_parent = storage.repos.is_parent_commit(
        db, project_id, left_hash, right_hash
    )
    if is_parent:
        # TODO LABEL RIGHT AS REGRESSION
        return
    else:
        test_hash = middle_select(db, project_id, left_hash, right_hash)
        middle_commit_id = storage.commits.add_or_get(
            db, project_id, test_hash)
        storage.results.update_preceding(db, right_commit_id, middle_commit_id)
        storage.results.update_following(db, left_commit_id, middle_commit_id)
        test_commit(
            db, project_id, test_id, test_hash, [config_id], preceding_commit_id=left_commit_id, following_commit_id=right_commit_id)
        return


def test_commit(
        db: Session,
        project_id: int,
        test_id: int,
        commit_hash: str,
        config_ids: List[str],
        preceding_commit_id: int = None,
        following_commit_id: int = None) -> int:

    commit_id = storage.commits.add_or_get(db, project_id, commit_hash)
    project_name = storage.projects.id2name(db, project_id)
    tester_env = storage.projects.id2tester_command(db, project_id)

    app_image_name = k8s.build_commit(db, project_name, commit_hash)
    for config_id in config_ids:
        result_id = storage.results.add_empty(
            db, config_id, commit_id, preceding_commit_id, following_commit_id)
        storage.tests.add_result_to_test(db, test_id, result_id)
        k8s.run_container_test(db, project_id,
                               tester_env, config_id, result_id, app_image_name)
    return
