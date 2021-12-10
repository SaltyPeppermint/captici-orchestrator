from typing import Dict, List, Optional
from pydantic import BaseModel
from test_orchestrator.k8s_interaction import container_spawn
from test_orchestrator.storage import projects, configs


class CommitTestReport(BaseModel):
    individual_results: Dict[int, str]
    is_regression: bool
    regressing_config: Optional[List[int]] = None


def test(project_id: int, commit: str, app_configs: List[Dict[str, str]]) -> int:
    project_name = projects.id2name(project_id)
    tester_env = projects.id2tester_env(project_id)
    container_spawn.build_commit(project_name, commit)
    container_spawn.run_tests(project_id, commit, tester_env, app_configs)
    test_id = 0
    # TODO Implement actual test_id Generation
    return test_id


def does_test_exist(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True


def is_test_finished(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True


def get_test_report(project_id: int, test_id: int) -> CommitTestReport:
    test_report = CommitTestReport(individual_results={
                                   2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    return test_report
