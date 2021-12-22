from typing import Dict, List

from cdpb_test_orchestrator import storage
from cdpb_test_orchestrator.data_objects import ResultParser, TestResponse

from . import parsing


def rel_diff(x: float, y: float) -> float:
    return abs(x - y) / max(x, y)


def bugs_in_project(db, project_id, threshold) -> List[int]:
    test_ids = storage.cdpb_tests.project_id2ids(db, project_id)
    return bugs_in_interval(db, project_id, threshold, test_ids)


def bugs_in_interval(db, project_id, threshold, test_ids):
    parser = storage.projects.id2parser(db, project_id)
    tests_with_bugs = []
    for test_id in test_ids:
        result = storage.cdpb_tests.id2result(db, test_id)

        preceding_id = storage.cdpb_tests.id2preceding_id(db, test_id)
        if preceding_id:
            preceding_result = storage.cdpb_tests.id2result(db, preceding_id)
            if preceding_result:
                if is_bug_between(parser, threshold, preceding_result, result):
                    tests_with_bugs.append(test_id)

        following_id = storage.cdpb_tests.id2following_id(db, test_id)
        if following_id:
            following_result = storage.cdpb_tests.id2result(db, following_id)
            if following_result:
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
        project_id = storage.cdpb_tests.id2project_id(db, test_id)
        parser = storage.projects.id2parser(db, project_id)
        preceding_id = storage.cdpb_tests.id2preceding_id(db, test_id)
        if preceding_id:
            test_result = storage.cdpb_tests.id2result(db, test_id)
            test_perf = parsing.result2value(test_result, parser)

            preceding_result = storage.cdpb_tests.id2result(db, preceding_id)
            preceding_perf = parsing.result2value(preceding_result, parser)

            return_dict[test_id] = rel_diff(preceding_perf, test_perf)
        else:
            return_dict[test_id] = 0

    return return_dict


def testing_report(db, test_group_id) -> TestResponse:
    test_ids_in_group = storage.cdpb_test_in_group.test_group_id2test_ids(
        db, test_group_id
    )
    project_id = storage.cdpb_test_groups.id2project_id(db, test_group_id)
    threshold = storage.cdpb_test_groups.id2threshold(db, test_group_id)
    bugs_in_group = bugs_in_interval(db, project_id, threshold, test_ids_in_group)

    if bugs_in_group is []:
        return TestResponse(
            individual_results=get_diffs(db, test_ids_in_group), bug_found=False
        )
    else:
        regressing_configs = list(
            map(storage.cdpb_tests.id2config_id, db, bugs_in_group)
        )
        return TestResponse(
            individual_results=get_diffs(db, test_ids_in_group),
            bug_found=True,
            regressing_config=regressing_configs,
        )
    # test_report = TestResponse(individual_results={
    #    2: "AS", 3: "asdf"}, bug_found = True, regressing_config = [2, 3])
    return test_group_id
