from typing import Tuple

from cdpb_test_orchestrator import k8s, storage
from cdpb_test_orchestrator.cdpb_testing import evaluate
from cdpb_test_orchestrator.data_objects import (
    CommitTestRequest,
    Project,
    ProjectTestRequest,
)
from sqlalchemy.orm import Session

from .selection import commits, configs


def test_commit(
    db: Session, project_id: int, test_group_id: int, req: CommitTestRequest
) -> None:
    project = storage.projects.id2project(db, project_id)
    tests_with_bugs = evaluate.bugs_in_project(db, project_id, req.threshold)

    tar_path = storage.tars.tar_into(project, req.commit_hash)
    app_image_name = k8s.build_commit(tar_path, project_id, req.commit_hash)

    bug_hash_dict = {}
    for test_id in tests_with_bugs:
        bug_hash_dict[test_id] = storage.cdpb_tests.id2commit_hash(db, test_id)

    preceding_tests = configs.select_configs(
        project, req.n_configs, bug_hash_dict, req.selection_strategy
    )

    for preceding_test in preceding_tests:
        preceding_test_id = preceding_test[1]
        config_id = storage.cdpb_tests.id2config_id(db, preceding_test_id)
        test_id = storage.cdpb_tests.add_empty(
            db, project_id, config_id, req.commit_hash, preceding_test_id, None
        )

        storage.cdpb_test_in_group.add_test_to_group(db, test_id, test_group_id)
        config_content = storage.configs.id2content(db, config_id)
        k8s.run_test(project, config_content, test_id, test_group_id, app_image_name)
    return


def test_whole_project(
    db: Session, project_id: int, test_group_id: int, req: ProjectTestRequest
) -> None:
    project = storage.projects.id2project(db, project_id)
    commit_hashs = commits.initial_sample_select(
        project.name, project_id, req.n_commits
    )

    app_image_names = {}
    for commit_hash in commit_hashs:
        tar_path = storage.tars.tar_into(project, commit_hash)
        app_image_names[commit_hash] = k8s.build_commit(
            tar_path, project_id, commit_hash
        )

    config_ids = storage.cdpb_tests.project_id2ids(db, project_id)

    for config_id in config_ids:
        preceding_test_id = None
        for commit_hash in commit_hashs:
            test_id = storage.cdpb_tests.add_empty(
                db, project_id, config_id, commit_hash, preceding_test_id, None
            )
            storage.cdpb_test_in_group.add_test_to_group(db, test_id, test_group_id)

            if preceding_test_id is not None:
                storage.cdpb_tests.update_following(db, preceding_test_id, test_id)
            preceding_test_id = test_id

            app_image_name = app_image_names[commit_hash]
            config_content = storage.configs.id2content(db, config_id)
            k8s.run_test(
                project, config_content, test_id, test_group_id, app_image_name
            )
    return


def report_action(db: Session, test_group_id: int, test_id: int) -> None:
    project_id = storage.cdpb_tests.id2project_id(db, test_id)
    project = storage.projects.id2project(db, project_id)

    config_id = storage.cdpb_tests.id2config_id(db, test_id)
    commit_hash = storage.cdpb_tests.id2commit_hash(db, test_id)

    result = storage.cdpb_tests.id2result(db, test_id)
    threshold = storage.cdpb_test_groups.id2threshold(db, test_group_id)

    preceding_id = storage.cdpb_tests.id2preceding_id(db, test_id)
    if preceding_id:
        preceding_commit_hash = storage.cdpb_tests.id2commit_hash(db, preceding_id)
        preceding_result = storage.cdpb_tests.id2result(db, preceding_id)
        if evaluate.bug_in_interval(
            project,
            preceding_commit_hash,
            preceding_result,
            commit_hash,
            result,
            threshold,
        ):
            spawn_test_between(
                db,
                project,
                test_group_id,
                config_id,
                preceding_id,
                preceding_commit_hash,
                test_id,
                commit_hash,
            )

    following_id = storage.cdpb_tests.id2following_id(db, test_id)
    if following_id:
        following_commit_hash = storage.cdpb_tests.id2commit_hash(db, following_id)
        following_result = storage.cdpb_tests.id2result(db, following_id)
        if evaluate.bug_in_interval(
            project,
            commit_hash,
            result,
            following_commit_hash,
            following_result,
            threshold,
        ):
            spawn_test_between(
                db,
                project,
                test_group_id,
                config_id,
                test_id,
                commit_hash,
                following_id,
                following_commit_hash,
            )
    return


def get_test_meta(db: Session, test_id: int) -> Tuple[Project, int, str, str]:
    project_id = storage.cdpb_tests.id2project_id(db, test_id)
    project = storage.projects.id2project(db, project_id)

    config_id = storage.cdpb_tests.id2config_id(db, test_id)
    commit_hash = storage.cdpb_tests.id2commit_hash(db, test_id)
    result = storage.cdpb_tests.id2result(db, test_id)
    return project, config_id, commit_hash, result


def spawn_test_between(
    db: Session,
    project: Project,
    test_group_id: int,
    config_id: int,
    preceding_id: int,
    preceding_commit_hash: str,
    following_id: int,
    following_commit_hash: str,
) -> None:
    # irrelevant if preceding or following, both have same id
    commit_hash = commits.middle_select(
        project.name, project.id, preceding_commit_hash, following_commit_hash
    )
    test_id = storage.cdpb_tests.add_empty(
        db, project.id, config_id, commit_hash, preceding_id, following_id
    )
    storage.cdpb_test_in_group.add_test_to_group(db, test_id, test_group_id)
    # double linked list, redirect pointers
    storage.cdpb_tests.update_preceding(db, following_id, test_id)
    storage.cdpb_tests.update_following(db, preceding_id, test_id)

    project = storage.projects.id2project(db, project.id)

    tar_path = storage.tars.tar_into(project, commit_hash)
    app_image_name = k8s.build_commit(tar_path, project.id, commit_hash)
    config_content = storage.configs.id2content(db, config_id)
    k8s.run_test(project, config_content, test_id, test_group_id, app_image_name)

    return