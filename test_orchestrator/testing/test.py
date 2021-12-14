from typing import List

import k8s
import storage
from api.request_bodies import TestRequest
from sqlalchemy.orm import Session

from .selection.commits import select_commits
from .selection.configs import select_configs


def test_multiple_commits(
        db: Session,
        project_id: int,
        req: TestRequest) -> int:
    test_id = storage.tests.add(db, project_id)

    commits_hashs_to_test = select_commits(
        db,
        project_id,
        req.first_commit_hash,
        req.last_commit_hash,
        req.n_commits
    )
    configs_to_test = select_configs(
        db,
        project_id,
        req.n_configs,
        req.selection_strategy
    )
    for commit_hash in commits_hashs_to_test:
        test_single_commit(
            db,
            project_id,
            test_id,
            commit_hash,
            configs_to_test
        )
    return test_id


def test_single_commit(
        db: Session,
        project_id: int,
        test_id: int,
        commit_hash: str,
        config_ids: List[str]) -> int:

    commit_id = storage.commits.add_or_update(db, project_id, commit_hash)
    project_name = storage.projects.id2name(db, project_id)
    tester_env = storage.projects.id2tester_command(db, project_id)

    k8s.build_commit(db, project_name, commit_hash)
    for config_id in config_ids:
        result_id = storage.results.add_empty(db, config_id, commit_id)
        storage.tests.add_result_to_test(db, test_id, result_id)
        k8s.run_test(
            db,
            project_id,
            commit_hash,
            tester_env,
            config_id,
            result_id
        )
    return
