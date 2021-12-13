from typing import List
from test_orchestrator import storage


def select(project_id: int, n_configs: int) -> List[int]:
    print("Ignoring number and returning all configs")
    return storage.configs.project_id2config_ids(project_id)
