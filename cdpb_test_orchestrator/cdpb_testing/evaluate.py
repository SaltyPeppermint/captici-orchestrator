from typing import Dict, List

from cdpb_test_orchestrator import storage
from cdpb_test_orchestrator.data_objects import (
    RegressionResponse,
    ResultParser,
    TestResponse,
)

from . import parsing


def rel_diff(x: float, y: float) -> float:
    return abs(x - y) / max(x, y)


def rel_diff_of_test_ids(db, project_id, test_ids):
    parser = storage.projects.id2parser(db, project_id)
    tests_with_bugs = {}
    for test_id in test_ids:
        result = storage.cdpb_tests.id2result(db, test_id)

        preceding_id = storage.cdpb_tests.id2preceding_id(db, test_id)
        if preceding_id:
            preceding_result = storage.cdpb_tests.id2result(db, preceding_id)
            if preceding_result:
                diff = diff_between_results(parser, result, preceding_result)
                tests_with_bugs[test_id] = diff
        # Following not needed since a detectable bug always needs a preceding
        # result to compare to
        #
        # following_id = storage.cdpb_tests.id2following_id(db, test_id)
        # if following_id:
        #     following_result = storage.cdpb_tests.id2result(db, following_id)
        #     if following_result:
        #         if is_bug_between(parser, threshold, result, following_result):
        #             tests_with_bugs.append(following_id)
    # deduplicate
    return tests_with_bugs


def bugs_in_rel_diffs(ids_with_diffs: Dict[int, float], threshold: float) -> List[int]:
    return [k for k, v in ids_with_diffs.items() if v > threshold]


def bug_ids_in_project(db, project_id, threshold) -> List[int]:
    test_ids = storage.cdpb_tests.project_id2ids(db, project_id)
    test_ids_with_rel_diff = rel_diff_of_test_ids(db, project_id, test_ids)
    return bugs_in_rel_diffs(test_ids_with_rel_diff, threshold)


def diff_between_results(parser: ResultParser, result_a: str, result_b: str) -> float:
    value_a = parsing.result2value(result_a, parser)
    value_b = parsing.result2value(result_b, parser)
    return rel_diff(value_a, value_b)


def is_bug_between_results(
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
    test_ids = storage.cdpb_test_in_group.test_group_id2test_ids(db, test_group_id)
    project_id = storage.cdpb_test_groups.id2project_id(db, test_group_id)
    threshold = storage.cdpb_test_groups.id2threshold(db, test_group_id)
    test_ids_with_rel_diffs = rel_diff_of_test_ids(db, project_id, test_ids)
    test_ids_with_bugs_in_group = bugs_in_rel_diffs(test_ids_with_rel_diffs, threshold)

    if len(test_ids_with_bugs_in_group) == 0:
        return TestResponse(
            project_id=project_id,
            bug_found=False,
            individual_results=test_ids_with_rel_diffs,
        )
    else:
        regressions = []
        for test_id in test_ids_with_bugs_in_group:
            config_id = storage.cdpb_tests.id2config_id(db, test_id)
            regressions.append(
                RegressionResponse(
                    test_id=test_id,
                    commit_hash=storage.cdpb_tests.id2commit_hash(db, test_id),
                    config_id=config_id,
                    config_content=storage.configs.id2content(db, config_id),
                    regression=test_ids_with_rel_diffs[test_id],
                )
            )

        return TestResponse(
            project_id=project_id,
            bug_found=True,
            individual_results=test_ids_with_rel_diffs,
            regressions=regressions,
        )
    # test_report = TestResponse(individual_results={
    #    2: "AS", 3: "asdf"}, bug_found = True, regressing_config = [2, 3])
    return test_group_id
