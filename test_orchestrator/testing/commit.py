from typing import List, Optional, Tuple


class CommitTestReport:
    individual_results: List[Tuple(int, str)]
    is_regression: bool
    regressing_config: Optional[List[int]]


def test(project_id: int, commit: str) -> int:
    test_id = 0
    return test_id


def does_test_exist(project_id: int, test_id: int) -> bool:
    return True


def is_test_finished(project_id: int, test_id: int) -> bool:
    return True


def get_test_report(project_id: int, test_id: int) -> int:
    test_report = CommitTestReport()
    return test_report
