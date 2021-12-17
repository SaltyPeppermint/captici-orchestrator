from test_orchestrator.api.request_bodies import ResultParser

from . import demo


def result2value(report: str, parser_type: ResultParser) -> float:
    if parser_type == ResultParser.JUNIT:
        return demo.result2value(report)
    else:
        raise AttributeError("Parser not supported.")
