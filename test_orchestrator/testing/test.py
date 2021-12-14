from enum import Enum
from typing import List

from sqlalchemy.orm import Session
from test_orchestrator.api.request_bodies import TestRequest
from test_orchestrator import k8s
from test_orchestrator import storage
from .selection import commits, configs


def test_multiple_commits(db: Session, project_id: int, testing_request: TestRequest) -> int:
    first_commit_hash = testing_request.first_commit_hash
    commits_to_test = commits.select_commits(
        project_id, first_commit_hash, testing_request.first_commit_hash, testing_request.last_commit_hash, testing_request.n_commits)
    configs_to_test = configs.select_configs(
        db, project_id, testing_request.n_configs, testing_request.selection_strategy)
    return 4


def test_single_commit(
        db: Session, project_id: int, commit_hash: str, config_ids: List[str]) -> int:

    project_name = storage.projects.id2name(db, project_id)
    tester_env = storage.projects.id2tester_command(db, project_id)

    k8s.build_commit(db, project_name, commit_hash)
    for config_id in config_ids:
        result_id = storage.results.add(db, config_id, result_id)
        k8s.run_test(db, project_id, commit_hash,
                     tester_env, config_id, result_id)
    test_id = 0
    # TODO Implement actual test_id Generation
    return test_id
