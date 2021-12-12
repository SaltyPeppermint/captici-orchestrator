import unittest
import context

# nopep8


class TestMain(unittest.TestCase):
    def test_demo_parser(self):
        from test_orchestrator.testing.evaluation.report_parsing import demo
        junit = '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" failures="0" skipped="0" tests="1" time="1.038" timestamp="2021-12-10T16:20:31.361154" hostname="ThinkPad-T495"><testcase classname="tests.test_demo.TestMain" name="test_run" time="1.002" /></testsuite></testsuites>'
        self.assertEqual(demo.report2value(junit), 1.002)


if __name__ == "__main__":
    unittest.main(verbosity=2)
