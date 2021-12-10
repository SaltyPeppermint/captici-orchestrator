import pickle
from typing import Dict, Iterable, List, Optional

from pydantic.main import BaseModel


class Report(BaseModel):
    individual_results: Dict[int, str]
    is_regression: bool
    regressing_config: Optional[List[int]] = None


class ReportMeta:
    def __init__(self, project_id: int, commit: str, test_id: int):
        self.project_id = project_id
        self.commit = commit
        self.test_id = test_id

    def serialize(self) -> str:
        return pickle.dumps(self).encode("base64", "strict")

    @classmethod
    def deserialize(cls, report_id):
        return cls(pickle.loads(report_id.decode("base64", "strict")))

    def __iter__(self) -> Iterable:
        yield self.project_id
        yield self.commit
        yield self.test_id


def add(report_id: str, report_content: str):
    project_id, commit, test_id = ReportMeta.deserialize(report_id)
    return True


def get_test_report(project_id: int, test_id: int) -> Report:
    test_report = Report(individual_results={
        2: "AS", 3: "asdf"}, is_regression=True, regressing_config=[2, 3])
    return test_report
