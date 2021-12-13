import math
from typing import List, Tuple

from . import report_parsing


def rel_diff(x: float, y: float) -> float:
    return math.abs(x - y) / max(x, y)


def detect_regressions(reports: List[Tuple[str, str]]):
    for report in reports:
        report_metadata, performance = report_parsing.parse_report(report)
        # TODO
        # Immer zwei parsen, storen, und comparen. Falls regression zu ner liste hinzufügen und die dann zurück geben.
        # Vorteil: Kann auch für nur zwei gebraucht werden.
        #
    return  # dummy
