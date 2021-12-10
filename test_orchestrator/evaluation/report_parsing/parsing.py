
from typing import List, Tuple

from test_orchestrator import storage
from . import demo


def report2value(report: str, project_id: int) -> float:
    type = storage.projects.id2type(project_id)
    if(type == storage.projects.ProjectType.DEMO):
        return demo.report2value(report)
    else:
        raise AttributeError("What kind of Project Type are you running?")


def reports2values(report: List[Tuple[str, str]]) -> List[Tuple[storage.ReportMeta, float]]:
    report_info = storage.Report.deserialize(report[0])
    performance = report2value(report[1])
    return report_info, performance
    # TODO add return annotation
