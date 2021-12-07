from typing import Tuple
from storage import reports
import storage.configs
import storage.projects


def accept_report(report_identifier: str, report_content: str):
    project_id, commit_hash, test_id = reports.deserialize_id()
    return True
