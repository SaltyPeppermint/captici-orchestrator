from typing import List, Optional

from sqlalchemy.orm import Session
from test_orchestrator import k8s, storage
from test_orchestrator.api import request_bodies

from .selection import commits, configs


def test_commit(
        db: Session,
        project_id: int,
        test_group_id: int,
        req: request_bodies.CommitTestRequest) -> int:

    to_test = configs.select_configs(
        db, project_id, req.n_configs, req.selection_strategy)
    project_name = storage.projects.id2name(db, project_id)
    app_image_name = k8s.build_commit(
        project_name, project_id, req.commit_hash)

    for preceding_commit_hash, config_id in to_test:
        test_id = storage.tests.add_empty(
            db, config_id, req.commit_hash, preceding_commit_hash, None)

        storage.test_in_test_group.add_test_to_test_group(
            db, test_id, test_group_id)

        k8s.run_container_test(db, project_id, config_id,
                               test_id, test_group_id, app_image_name)
    return


def test_whole_project(
        db: Session,
        project_id: int,
        test_group_id: int,
        req: request_bodies.ProjectTestRequest) -> int:

    commit_hashs = commits.initial_sample_select(
        db, project_id, req.n_commits)
    config_ids = storage.config.project_id2ids(db, project_id)
    for i, commit_hash in enumerate(commit_hashs):
        preceding_commit_hash, following_commit_hash = commits.assign_bounds(
            commit_hashs, i)

        project_name = storage.projects.id2name(db, project_id)
        app_image_name = k8s.build_commit(
            project_name, project_id, commit_hash)

        for config_id in config_ids:
            test_id = storage.tests.add_empty(
                db, config_id, commit_hash, preceding_commit_hash, following_commit_hash)
            project_name = storage.projects.id2name(db, test_id)
            storage.test_in_test_group.add_test_to_test_group(
                db, test_id, test_group_id)

            k8s.run_container_test(db, project_id, config_id,
                                   test_id, test_group_id, app_image_name)
    return


def spawn_test_between(
        db: Session,
        project_id: int,
        test_group_id: int,
        config_id: int,
        preceding_commit_hash: int,
        following_commit_hash: int) -> int:

    commit_hash = commits.middle_select(
        db, project_id, preceding_commit_hash, following_commit_hash)
    test_id = storage.tests.add_empty(
        db, config_id, commit_hash, preceding_commit_hash, following_commit_hash)
    storage.test_in_test_groups.add_test_to_test_group(
        db, test_id, test_group_id)
    storage.tests.update_preceding(db, preceding_commit_hash, commit_hash)
    storage.tests.update_following(db, following_commit_hash, commit_hash)

    project_name = storage.projects.id2name(db, test_id)
    app_image_name = k8s.build_commit(project_name, project_id, commit_hash)
    k8s.run_container_test(db, project_id, config_id,
                           test_id, test_group_id, app_image_name)
    return
