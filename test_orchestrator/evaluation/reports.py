from test_orchestrator.storage import reports, configs, projects


def accept_report(report_identifier: str, report_content: str):
    project_id, commit_hash, test_id = reports.deserialize_id()
    return True
