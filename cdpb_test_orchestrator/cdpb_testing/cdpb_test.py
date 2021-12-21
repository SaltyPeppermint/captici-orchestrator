import logging
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

logger = logging.getLogger("uvicorn")


def test_commit(db: Session, test_group_id: int, req: CommitTestRequest) -> None:
    logger.info(
        f"New commit test of project {req.project_id} requested "
        f"under the test group {test_group_id}"
    )
    project = storage.projects.id2project(db, req.project_id)
    tests_with_bugs = evaluate.bugs_in_project(db, req.project_id, req.threshold)
    logger.info(f"Previous bugs found in the test {tests_with_bugs}.")

    tar_path = storage.tars.tar_into(project, req.commit_hash)
    app_image_name = k8s.build_commit(tar_path, project, req.commit_hash)
    logger.info(f"Built image of the new commit {app_image_name}.")

    bug_hash_dict = {}
    for test_id in tests_with_bugs:
        bug_hash_dict[test_id] = storage.cdpb_tests.id2commit_hash(db, test_id)

    preceding_tests = configs.select_configs(
        project, req.n_configs, bug_hash_dict, req.selection_strategy
    )
    logger.info(f"Selected configs to test commit with {preceding_tests}.")

    for preceding_test in preceding_tests:
        preceding_test_id = preceding_test[1]
        config_id = storage.cdpb_tests.id2config_id(db, preceding_test_id)
        test_id = storage.cdpb_tests.add_empty(
            db, req.project_id, config_id, req.commit_hash, preceding_test_id, None
        )

        storage.cdpb_test_in_group.add_test_to_group(db, test_id, test_group_id)
        config_content = storage.configs.id2content(db, config_id)
        k8s.run_test(project, config_content, test_id, test_group_id, app_image_name)
        logger.info(f"Starting new commit test with config {config_id}.")
        logger.info(
            f"Started new commit test {test_id} with config {config_id} for "
            f"of {req.project_id} in the test group {test_group_id}."
        )
    logger.info(
        f"Started all new commit tests for new commit in {req.project_id} "
        f"in the test group {test_group_id}."
    )
    return


def test_whole_project(
    db: Session, test_group_id: int, req: ProjectTestRequest
) -> None:
    logger.info(
        f"Whole project test of project {req.project_id} requested "
        f"under the test group {test_group_id}"
    )
    project = storage.projects.id2project(db, req.project_id)
    commit_hashs = commits.initial_sample_select(project, req.n_commits)
    logger.info(f"Selected commits {commit_hashs} for initial test.")

    config_ids = storage.cdpb_tests.project_id2ids(db, req.project_id)
    logger.info(
        f"Testing all configs {config_ids} for initial test of {req.project_id}."
    )

    tar_paths = {}
    for commit_hash in commit_hashs:
        tar_paths[commit_hash] = storage.tars.tar_into(project, commit_hash)

    app_image_names = k8s.build_commits(req.project_id, project, tar_paths)

    for config_id in config_ids:
        preceding_test_id = None
        config_content = storage.configs.id2content(db, config_id)
        for commit_hash in commit_hashs:
            test_id = storage.cdpb_tests.add_empty(
                db, req.project_id, config_id, commit_hash, preceding_test_id, None
            )
            storage.cdpb_test_in_group.add_test_to_group(db, test_id, test_group_id)

            if preceding_test_id is not None:
                storage.cdpb_tests.update_following(db, preceding_test_id, test_id)
            preceding_test_id = test_id

            app_image_name = app_image_names[commit_hash]

            logger.info(
                f"Starting test {test_id} with config {config_id} for "
                f"initial testing of {req.project_id} "
                f"in the test group {test_group_id}."
            )
            k8s.run_test(
                project, config_content, test_id, test_group_id, app_image_name
            )

    logger.info(
        f"Started all initial tests for whole project test of {req.project_id}"
        f"in the test group {test_group_id}."
    )
    return


def report_action(db: Session, test_group_id: int, test_id: int) -> None:
    logger.info(f"Received report for test {test_id} in test_group {test_group_id}")
    logger.info(f"Deleteing now unused config map for test {test_id}")

    project_id = storage.cdpb_tests.id2project_id(db, test_id)
    project = storage.projects.id2project(db, project_id)
    config_id = storage.cdpb_tests.id2config_id(db, test_id)
    commit_hash = storage.cdpb_tests.id2commit_hash(db, test_id)

    result = storage.cdpb_tests.id2result(db, test_id)
    threshold = storage.cdpb_test_groups.id2threshold(db, test_group_id)
    logger.info(f"Evaluating with threshhold {threshold}.")

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
            logger.info(
                f"Bug before between the preceding commit {preceding_commit_hash} "
                f"and this one {commit_hash} and no parent relationship. "
                "Spawning test in between."
            )
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
            logger.info(
                f"Bug before between the following commit {following_commit_hash} "
                f"and this one {commit_hash} and no parent relationship. "
                "Spawning test in between."
            )
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
        project, preceding_commit_hash, following_commit_hash
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
    app_image_name = k8s.build_commit(tar_path, project, commit_hash)
    config_content = storage.configs.id2content(db, config_id)
    k8s.run_test(project, config_content, test_id, test_group_id, app_image_name)

    return
