import logging

from cdpb_test_orchestrator import k8s, storage
from cdpb_test_orchestrator.cdpb_testing import evaluate
from cdpb_test_orchestrator.data_objects import (
    CommitTestRequest,
    ProjectTestRequest,
    Test,
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
    tests_with_bugs = evaluate.bug_ids_in_project(db, req.project_id, req.threshold)
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

    config_ids = storage.configs.project_id2ids(db, req.project_id)
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


def test_preceding_bug(
    db: Session,
    old_test: Test,
    preceding_id: int,
    preceding_commit_hash: str,
    test_group_id: int,
):
    logger.info(
        f"Bug between the preceding commit {preceding_commit_hash} "
        f"and this one {old_test.commit_hash} "
        "and no parent relationship. Spawning test in between."
    )
    commit_hash = commits.middle_select(
        old_test.project, preceding_commit_hash, old_test.commit_hash
    )
    new_test_id = storage.cdpb_tests.add_empty(
        db,
        old_test.project.id,
        old_test.config_id,
        commit_hash,
        preceding_id,
        old_test.id,
    )
    storage.cdpb_test_in_group.add_test_to_group(db, new_test_id, test_group_id)
    # double linked list, redirect pointers
    storage.cdpb_tests.update_preceding(db, old_test.id, new_test_id)
    storage.cdpb_tests.update_following(db, preceding_id, new_test_id)

    tar_path = storage.tars.tar_into(old_test.project, commit_hash)
    app_image_name = k8s.build_commit(tar_path, old_test.project, commit_hash)
    k8s.run_test(
        old_test.project,
        old_test.config_content,
        new_test_id,
        test_group_id,
        app_image_name,
    )


def check_for_preceding_bug(
    db: Session, test_group_id: int, test: Test, threshold: float
) -> None:
    preceding_id = storage.cdpb_tests.id2preceding_id(db, test.project.id)
    if preceding_id is None:
        return

    preceding_result = storage.cdpb_tests.id2result(db, preceding_id)
    if preceding_result is None:
        return

    # return False if the preceding test has no result (yet)
    # This may happen because tests are run out of order
    # Since always preceding and following tests are considered in every test,
    # this isn't a problem
    if not evaluate.is_bug_between_results(
        test.project.parser, threshold, preceding_result, test.result
    ):
        return

    preceding_commit_hash = storage.cdpb_tests.id2commit_hash(db, preceding_id)
    if storage.repos.is_parent_commit(
        test.project, preceding_commit_hash, test.commit_hash
    ):
        return

    test_preceding_bug(db, test, preceding_id, preceding_commit_hash, test_group_id)
    return


def test_following_bug(
    db: Session,
    old_test: Test,
    following_id: int,
    following_commit_hash: str,
    test_group_id: int,
):
    logger.info(
        f"Bug between this commit {old_test.commit_hash} "
        f"and the following commit {following_commit_hash} "
        "and no parent relationship. Spawning test in between."
    )
    commit_hash = commits.middle_select(
        old_test.project, old_test.commit_hash, following_commit_hash
    )
    new_test_id = storage.cdpb_tests.add_empty(
        db,
        old_test.project.id,
        old_test.config_id,
        commit_hash,
        old_test.id,
        following_id,
    )
    storage.cdpb_test_in_group.add_test_to_group(db, new_test_id, test_group_id)
    # double linked list, redirect pointers
    storage.cdpb_tests.update_preceding(db, following_id, new_test_id)
    storage.cdpb_tests.update_following(db, old_test.id, new_test_id)

    tar_path = storage.tars.tar_into(old_test.project, commit_hash)
    app_image_name = k8s.build_commit(tar_path, old_test.project, commit_hash)
    k8s.run_test(
        old_test.project,
        old_test.config_content,
        new_test_id,
        test_group_id,
        app_image_name,
    )


def check_for_following_bug(
    db: Session, test_group_id: int, test: Test, threshold: float
) -> None:
    following_id = storage.cdpb_tests.id2following_id(db, test.id)
    if following_id is None:
        return

    following_result = storage.cdpb_tests.id2result(db, following_id)
    if following_result is None:
        # return False if the following has no result (yet)
        # This may happen because tests are run out of order
        # Since always preceding and following tests are considered in every test,
        # this isn't a problem
        return

    if not evaluate.is_bug_between_results(
        test.project.parser, threshold, test.result, following_result
    ):
        return

    following_commit_hash = storage.cdpb_tests.id2commit_hash(db, following_id)
    if storage.repos.is_parent_commit(
        test.project, test.commit_hash, following_commit_hash
    ):
        return

    test_following_bug(db, test, following_id, following_commit_hash, test_group_id)
    return


def report_action(db: Session, test_group_id: int, test: Test) -> None:
    logger.info(f"Received report for test {test.id} in test_group {test_group_id}")
    logger.info(f"Deleteing now unused config map for test {test.id}")
    k8s.delete_config_map(test.id)

    threshold = storage.cdpb_test_groups.id2threshold(db, test_group_id)
    logger.info(f"Evaluating with threshhold {threshold}.")

    check_for_preceding_bug(db, test_group_id, test, threshold)
    check_for_following_bug(db, test_group_id, test, threshold)
    return
