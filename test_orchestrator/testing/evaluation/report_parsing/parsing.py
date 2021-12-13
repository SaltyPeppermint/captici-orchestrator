
from typing import List, Tuple

from test_orchestrator import storage
from . import demo


def report2value(report: str, project_id: int) -> float:
    type = storage.projects.id2type(project_id)
    if(type == storage.projects.ProjectType.DEMO):
        return demo.report2value(report)
    else:
        raise AttributeError("What kind of Project Type are you running?")


# def serialized2values(ser_results: List[Tuple[str, str]]) -> List[Tuple[storage.ResultMetadata, float]]:
#     result_metadata = storage.ResultMetadata.deserialize(ser_results[0])
#     performance = report2value(ser_results[1])
#     return result_metadata, performance
#     # TODO add return annotation
