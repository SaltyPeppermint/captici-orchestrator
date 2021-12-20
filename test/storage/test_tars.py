import unittest

from cdpb_test_orchestrator.data_objects import Project, ResultParser
from cdpb_test_orchestrator.storage import tars


class TestTarInto(unittest.TestCase):
    def test_tar_into(self):
        repo_url = "https://git.informatik.uni-leipzig.de/bachelor-thesis-code/demo.git"
        project = Project(
            id=1,
            name="demo",
            tester_command="pytest",
            result_path="result",
            parser=ResultParser.JUNIT,
            repo_url=repo_url,
            git_user="git",
            auth_token="W4EZzCF5Ga9q1ooz8jzf",
            main_branch="main",
            dockerfile_path="./Dockerfile",
            config_path="/app/config/settings.ini",
            two_container=False,
        )
        commit_hash = "3ff73097efa92d32a19b09ec3ea113042d637ca2"
        tars.tar_into(project, commit_hash)
