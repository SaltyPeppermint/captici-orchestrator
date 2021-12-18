import unittest

from cdpb_test_orchestrator.cdpb_testing.parsing import parsing
from cdpb_test_orchestrator.data_objects import ResultParser


class TestMain(unittest.TestCase):
    def test_demo_parser(self):
        junit = (
            '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest"'
            ' errors="0" failures="0" skipped="0" tests="1" time="1.038"'
            ' timestamp="2021-12-10T16:20:31.361154" hostname="ThinkPad-T495"><testcase'
            ' classname="tests.test_demo.TestMain" name="test_run" time="1.002"'
            " /></testsuite></testsuites>"
        )
        self.assertEqual(parsing.result2value(junit, ResultParser.JUNIT), 1.002)


if __name__ == "__main__":
    unittest.main(verbosity=2)
