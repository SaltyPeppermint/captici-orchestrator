from test_orchestrator import storage
from test_orchestrator.api.request_bodies import Parser

from . import demo


def result2value(report: str, type: Parser) -> float:
    if(type == storage.projects.ProjectType.DEMO):
        return demo.report2value(report)
    else:
        raise AttributeError("What kind of Project Type are you running?")
