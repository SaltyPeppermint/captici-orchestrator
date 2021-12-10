from test_orchestrator.storage.projects import ProjectType
from test_orchestrator.storage import projects
from . import demo


def report2value(report: str, project_id: ProjectType) -> float:
    type = projects.id2type(project_id)
    if(type == ProjectType.DEMO):
        return demo.report2value(report)
    else:
        raise AttributeError("What kind of Project Type are you running?")
