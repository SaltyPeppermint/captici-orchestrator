import logging

from junitparser import Error, Failure, JUnitXml, Skipped

logger = logging.getLogger("uvicorn")


class JunitParsingError(ValueError):
    pass


class JunitParsingWarning(UserWarning):
    pass


def result2value(report: str) -> float:
    junit = JUnitXml.fromstring(report)
    total_time = 0.0
    for suite in junit:
        for case in suite:
            if case.result:
                parse_case(case)
            else:
                total_time += float(case.time)
    return total_time


def parse_case(case):
    logger.info(f"Parsing result {case.result}.")
    if isinstance(case.result, Error):
        raise JunitParsingError(
            "You're test raised an error according to Junit.", case.result.message
        )
    elif isinstance(case.result, Failure):
        raise JunitParsingError(
            "You're test failed according to Junit.", case.result.message
        )
    elif isinstance(case.result, Skipped):
        raise JunitParsingWarning(
            "You're skipped tests. You sure about that?", case.result.message
        )
    else:
        raise JunitParsingError(
            "You completely broke the junit, this should not be possible",
            case.result.message,
        )
