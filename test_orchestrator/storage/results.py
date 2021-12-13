import pickle
from typing import Dict, Iterable, List, Optional

from pydantic.main import BaseModel

from test_orchestrator.k8s.templates import config_map


def config_id2result_ids(config_id: int) -> List[int]:
    # TODO IMPLEMENT
    return [1, 5]


def result_id2commit_id(conifg_id: int) -> int:
    # TODO IMPLEMENT
    return 2

# class ResultMetadata:
#     def __init__(self, project_id: int, commit_hash: str, config_id: int):
#         self.project_id = project_id
#         self.commit_hash = commit_hash
#         self.config_id = config_id

#     def serialize(self) -> str:
#         return pickle.dumps(self).encode("base64", "strict")

#     @classmethod
#     def deserialize(cls, ser_result_metadata):
#         return cls(pickle.loads(ser_result_metadata.decode("base64", "strict")))

#     def __iter__(self) -> Iterable:
#         yield self.project_id
#         yield self.commit_hash
#         yield self.config_id

# def add(ser_result_metadata: str, result_content: str):
#     project_id, commit_hash, config_id = ResultMetadata.deserialize(
#         ser_result_metadata)
#     return True
