from typing import Dict, List, Optional
from pydantic import BaseModel
from test_orchestrator.kubernetes import container_build
from test_orchestrator.storage import projects


class CommitTestReport(BaseModel):
    individual_results: Dict[int, str]
    is_regression: bool
    regressing_config: Optional[List[int]] = None


def test(project_id: int, commit: str) -> int:
    project_name = projects.id2name(project_id)
    container_build.build_commit(project_name, commit)
    test_id = 0
    return test_id


def does_test_exist(project_id: int, test_id: int) -> bool:
    return True


def is_test_finished(project_id: int, test_id: int) -> bool:
    return True


def get_test_report(project_id: int, test_id: int) -> CommitTestReport:
    test_report = CommitTestReport(individual_results={
                                   2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    return test_report
