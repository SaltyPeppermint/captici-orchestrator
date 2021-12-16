import storage

from . import demo


def report2value(report: str, project_id: int) -> float:
    type = storage.projects.id2type(project_id)
    if(type == storage.projects.ProjectType.DEMO):
        return demo.report2value(report)
    else:
        raise AttributeError("What kind of Project Type are you running?")
