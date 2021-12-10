from typing import Iterable
import pickle


class ReportInfo:
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
    project_id, commit, test_id = ReportInfo.deserialize(report_id)
    return True
