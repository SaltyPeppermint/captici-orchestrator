from sqlalchemy.orm import Session
from test_orchestrator import k8s, storage
from test_orchestrator.api.request_bodies import CommitTestRequest, ProjectTestRequest
from test_orchestrator.testing import evaluate

from .selection import commits, configs


def test_commit(
    db: Session, project_id: int, test_group_id: int, req: CommitTestRequest
) -> None:
    tests_with_bugs = evaluate.bugs_in_project(db, project_id, req.threshold)
    preceding_tests = configs.select_configs(
        db, project_id, req.n_configs, tests_with_bugs, req.selection_strategy
    )
    app_image_name = k8s.build_commit(db, project_id, req.commit_hash)

    for preceding_test in preceding_tests:
        preceding_test_id = preceding_test[1]
        config_id = storage.tests.id2config_id(db, preceding_test_id)
        test_id = storage.tests.add_empty(
            db, project_id, config_id, req.commit_hash, preceding_test_id, None
        )

        storage.test_in_test_group.add_test_to_test_group(db, test_id, test_group_id)

        k8s.run_container_test(
            db, project_id, config_id, test_id, test_group_id, app_image_name
        )
    return


def test_whole_project(
    db: Session, project_id: int, test_group_id: int, req: ProjectTestRequest
) -> None:
    commit_hashs = commits.initial_sample_select(db, project_id, req.n_commits)

    app_image_names = {}
    for commit_hash in commit_hashs:
        app_image_names[commit_hash] = k8s.build_commit(db, project_id, commit_hash)

    config_ids = storage.tests.project_id2ids(db, project_id)

    for config_id in config_ids:
        preceding_test_id = None
        for commit_hash in commit_hashs:
            test_id = storage.tests.add_empty(
                db, project_id, config_id, commit_hash, preceding_test_id, None
            )
            storage.test_in_test_group.add_test_to_test_group(
                db, test_id, test_group_id
            )

            if preceding_test_id is not None:
                storage.tests.update_following(db, preceding_test_id, test_id)
            preceding_test_id = test_id

            app_image_name = app_image_names[commit_hash]
            k8s.run_container_test(
                db, project_id, config_id, test_id, test_group_id, app_image_name
            )
    return


def report_action(db: Session, test_group_id: int, test_id: int) -> None:
    project_id, parser, config_id, commit_hash, result = get_test_meta(db, test_id)
    threshold = storage.test_groups.id2threshold(db, test_group_id)

    preceding_id = storage.tests.id2preceding_id(db, test_id)
    if preceding_id:
        preceding_commit_hash = storage.tests.id2commit_hash(db, preceding_id)
        preceding_result = storage.tests.id2result(db, preceding_id)
        if evaluate.bug_in_interval(
            db,
            project_id,
            preceding_commit_hash,
            preceding_result,
            commit_hash,
            result,
            parser,
            threshold,
        ):
            spawn_test_between(
                db,
                project_id,
                test_group_id,
                config_id,
                preceding_id,
                preceding_commit_hash,
                test_id,
                commit_hash,
            )

    following_id = storage.tests.id2following_id(db, test_id)
    if following_id:
        following_commit_hash = storage.tests.id2commit_hash(db, following_id)
        following_result = storage.tests.id2result(db, following_id)
        if evaluate.bug_in_interval(
            db,
            project_id,
            commit_hash,
            result,
            following_commit_hash,
            following_result,
            parser,
            threshold,
        ):
            spawn_test_between(
                db,
                project_id,
                test_group_id,
                config_id,
                test_id,
                commit_hash,
                following_id,
                following_commit_hash,
            )
    return


def get_test_meta(db: Session, test_id: int):
    project_id = storage.tests.id2project_id(db, test_id)
    parser = storage.projects.id2parser(db, project_id)

    config_id = storage.tests.id2config_id(db, test_id)
    commit_hash = storage.tests.id2commit_hash(db, test_id)
    result = storage.tests.id2result(db, test_id)
    return project_id, parser, config_id, commit_hash, result


def spawn_test_between(
    db: Session,
    project_id: int,
    test_group_id: int,
    config_id: int,
    preceding_id: int,
    preceding_commit_hash: str,
    following_id: int,
    following_commit_hash: str,
) -> None:
    # irrelevant if preceding or following, both have same id
    commit_hash = commits.middle_select(
        db, project_id, preceding_commit_hash, following_commit_hash
    )
    test_id = storage.tests.add_empty(
        db, project_id, config_id, commit_hash, preceding_id, following_id
    )
    storage.test_in_test_group.add_test_to_test_group(db, test_id, test_group_id)
    # double linked list, redirect pointers
    storage.tests.update_preceding(db, following_id, commit_hash)
    storage.tests.update_following(db, preceding_id, commit_hash)

    app_image_name = k8s.build_commit(db, project_id, commit_hash)
    k8s.run_container_test(
        db, project_id, config_id, test_id, test_group_id, app_image_name
    )
    return
