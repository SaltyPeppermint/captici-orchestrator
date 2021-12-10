from typing import Dict, List
from test_orchestrator import k8s
from test_orchestrator.storage import projects, configs


def test(project_id: int, commit: str, app_configs: List[Dict[str, str]]) -> int:
    project_name = projects.id2name(project_id)
    tester_env = projects.id2tester_env(project_id)
    k8s.build_commit(project_name, commit)
    k8s.run_tests(project_id, commit, tester_env, app_configs)
    test_id = 0
    # TODO Implement actual test_id Generation
    return test_id


def does_test_exist(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True


def is_test_finished(project_id: int, test_id: int) -> bool:
    # TODO Implement
    return True
