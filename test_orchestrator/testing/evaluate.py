import math
from typing import List, Tuple

from sqlalchemy.orm import Session
from test_orchestrator import k8s, storage
from test_orchestrator.api import project
from test_orchestrator.api.request_bodies import Parser
from test_orchestrator.settings import config
from test_orchestrator.testing import test
from test_orchestrator.testing.selection import commits

from . import parsing


def rel_diff(x: float, y: float) -> float:
    return math.abs(x - y) / max(x, y)


def detect_regressions(results: List[Tuple[str, str]]):
    for result in results:
        report_metadata, performance = parsing.report2value(result)
        # TODO
        # Immer zwei parsen, storen, und comparen. Falls regression zu ner liste hinzufügen und die dann zurück geben.
        # Vorteil: Kann auch für nur zwei gebraucht werden.
        #
    return  # dummy


def is_bug_between(
        parser: Parser,
        threshold: float,
        result_a: str,
        result_b: int) -> bool:
    value_a = parsing.result2value(result_a, parser)
    value_b = parsing.result2value(result_b, parser)
    return rel_diff(value_a, value_b) > threshold


def bug_in_interval(
        db: Session,
        left_commit_hash: str,
        right_commit_hash: str,
        parser: int,
        config_id: int,
        threshold: float):

    parent_relationship = storage.repos.is_parent_commit(
        left_commit_hash, right_commit_hash)
    if not parent_relationship:
        left_commit_result = storage.tests.config_id_and_hash2result(
            db, config_id, left_commit_hash)
        right_commit_result = storage.tests.config_id_and_hash2result(
            db, config_id, right_commit_hash)
        bug_between = is_bug_between(
            parser, threshold, left_commit_result, right_commit_result)
        if bug_between and not parent_relationship:
            return True
    return False


def report_action(
        db: Session,
        test_group_id: float,
        test_id: int) -> int:

    project_id, parser, config_id, commit_hash = get_test_meta(db, test_id)
    threshold = storage.test_groups.id2threshold(db, test_group_id)

    preceding_commit_hash = storage.tests.id2preceding_commit_hash(db, test_id)
    if preceding_commit_hash:
        if bug_in_interval(
                db, preceding_commit_hash, commit_hash, parser, config_id, threshold):
            test.spawn_test_between(db, project_id, test_group_id, parser,
                                    preceding_commit_hash, commit_hash)

    following_commit_hash = storage.tests.id2following_commit_hash(
        db, test_id)
    if following_commit_hash:
        if bug_in_interval(
                db, commit_hash, preceding_commit_hash, parser, config_id, threshold):
            test.spawn_test_between(db, project_id, test_group_id, config_id,
                                    commit_hash, preceding_commit_hash)
    return


def get_test_meta(db: Session, test_id: int):
    project_id = storage.tests.id2project_id(db, test_id)
    parser = storage.projects.id2parser(db, project_id)

    config_id = storage.tests.id2config_id(db, test_id)
    commit_hash = storage.tests.id2commit_hash(db, test_id)
    return project_id, parser, config_id, commit_hash
