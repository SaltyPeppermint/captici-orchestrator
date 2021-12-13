from enum import Enum
from typing import List
from test_orchestrator.api.request_bodies import TestRequest
from test_orchestrator import k8s
from test_orchestrator import storage
from . import commits, configs


def test_multiple_commits(project_id: int, testing_request: TestRequest) -> int:
    first_commit_hash = testing_request.first_commit_hash
    commits_to_test = commits.select_commits(
        project_id, first_commit_hash, testing_request.first_commit_hash, testing_request.last_commit_hash, testing_request.n_commits)
    configs_to_test = configs.select_configs(
        project_id, testing_request.n_configs, testing_request.selection_strategy)
    return 4


def test_single_commit(
        project_id: int, commit_hash: str, app_configs: List[str]) -> int:

    project_name = storage.projects.id2name(project_id)
    tester_env = storage.projects.id2tester_env(project_id)
    k8s.build_commit(project_name, commit_hash)
    k8s.run_tests(project_id, commit_hash, tester_env, app_configs)
    test_id = 0
    # TODO Implement actual test_id Generation
    return test_id
