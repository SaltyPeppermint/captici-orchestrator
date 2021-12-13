

from test_orchestrator.api.response_bodies import TestResponse


def get_test_report(project_id: int, test_id: int) -> TestResponse:
    test_report = TestResponse(individual_results={
        2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    # TODO IMPLEMENT
    return test_report


def does_test_exist(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True


def is_test_finished(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True
