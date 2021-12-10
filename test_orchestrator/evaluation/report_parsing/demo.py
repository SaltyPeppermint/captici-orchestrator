from junitparser import JUnitXml, Failure, Skipped, Error


class JunitParsingError(ValueError):
    pass


class JunitParsingWarning(UserWarning):
    pass


def report2value(report: str) -> float:
    junit = JUnitXml.fromstring(report)
    total_time = 0
    for suite in junit:
        # print(suite)
        for case in suite:
            print(type(case))
            # print(case.name)
            # print(case.time)
            if case.result:
                print(case.result)
                if isinstance(case.result, Error):
                    raise JunitParsingError(
                        "You're test raised an error according to Junit. You have bigger problems than performance.", case.result.message)
                elif isinstance(case.result, Failure):
                    raise JunitParsingError(
                        "You're test failed according to Junit. You have bigger problems than performance.", case.result.message)
                elif isinstance(case.result, Skipped):
                    raise JunitParsingWarning(
                        "You're skipped tests. You sure about that?", case.result.message)
                else:
                    raise JunitParsingError(
                        "You completely broke the junit, this result should not be possible.Congratulations!", case.result.message)
            else:
                total_time += float(case.time)
    return total_time
