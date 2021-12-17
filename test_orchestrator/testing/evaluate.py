from typing import Dict, List

from sqlalchemy.orm import Session
from test_orchestrator import storage
from test_orchestrator.api.request_bodies import ResultParser
from test_orchestrator.api.response_bodies import TestResponse


from . import parsing


def rel_diff(x: float, y: float) -> float:
    return abs(x - y) / max(x, y)


def bugs_in_project(db, project_id, threshold) -> List[int]:
    test_ids = storage.tests.project_id2ids(db, project_id)
    parser = storage.projects.id2parser(db, project_id)
    tests_with_bugs = []
    for test_id in test_ids:
        result = storage.tests.id2result(db, test_id)

        preceding_id = storage.tests.id2preceding_id(db, test_id)
        if preceding_id:
            preceding_result = storage.tests.id2result(db, preceding_id)
            if is_bug_between(parser, threshold, preceding_result, result):
                tests_with_bugs.append(test_id)

        following_id = storage.tests.id2following_id(db, test_id)
        if following_id:
            following_result = storage.tests.id2result(db, following_id)
            if is_bug_between(parser, threshold, result, following_result):
                tests_with_bugs.append(following_id)
    # deduplicate
    return list(set(tests_with_bugs))


def is_bug_between(
    parser: ResultParser, threshold: float, result_a: str, result_b: str
) -> bool:
    value_a = parsing.result2value(result_a, parser)
    value_b = parsing.result2value(result_b, parser)
    return rel_diff(value_a, value_b) > threshold


def get_diffs(db, test_ids_in_group: List[int]) -> Dict[int, float]:
    return_dict = {}
    for test_id in test_ids_in_group:
        project_id = storage.tests.id2project_id(db, test_id)
        parser = storage.projects.id2parser(db, project_id)
        preceding_id = storage.tests.id2preceding_id(db, test_id)
        if preceding_id:
            test_result = storage.tests.id2result(db, test_id)
            test_perf = parsing.result2value(test_result, parser)

            preceding_result = storage.tests.id2result(db, preceding_id)
            preceding_perf = parsing.result2value(preceding_result, parser)

            return_dict[test_id] = rel_diff(preceding_perf, test_perf)
        else:
            return_dict[test_id] = 0

    return return_dict


def testing_report(db, test_group_id) -> TestResponse:
    test_ids_in_group = storage.test_in_test_group.test_group_id2test_ids(
        db, test_group_id
    )
    project_id = storage.test_groups.id2project_id(db, test_group_id)
    threshold = storage.test_groups.id2threshold(db, test_group_id)
    bugs_in_group = [
        t for t in test_ids_in_group if t in bugs_in_project(db, project_id, threshold)
    ]

    if bugs_in_group is []:
        return TestResponse(
            individual_results=get_diffs(db, test_ids_in_group), bug_found=False
        )
    else:
        regressing_configs = list(map(storage.tests.id2config_id, db, bugs_in_group))
        return TestResponse(
            individual_results=get_diffs(db, test_ids_in_group),
            bug_found=True,
            regressing_config=regressing_configs,
        )
    # test_report = TestResponse(individual_results={
    #    2: "AS", 3: "asdf"}, bug_found = True, regressing_config = [2, 3])
    return test_group_id


def bug_in_interval(
    db: Session,
    project_id: int,
    preceding_commit_hash: str,
    preceding_test_result: str,
    following_commit_hash: str,
    following_test_result: str,
    parser: ResultParser,
    threshold: float,
):
    parent_relationship = storage.repos.is_parent_commit(
        db, project_id, preceding_commit_hash, following_commit_hash
    )
    if not parent_relationship:
        bug_between = is_bug_between(
            parser, threshold, preceding_test_result, following_test_result
        )
        if bug_between and not parent_relationship:
            return True
    return False
