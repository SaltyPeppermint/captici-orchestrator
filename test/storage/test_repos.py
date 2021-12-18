import os
import subprocess
import unittest

from cdpb_test_orchestrator.storage import repos


class TestAuthInfo2CloneUrl(unittest.TestCase):
    def test_no_user_no_pw(self):
        git_url = "https://github.com/BurntSushi/ripgrep"
        git_user = "git"
        git_pw = None
        clone_url = repos.auth_info2clone_url(git_url, git_user, git_pw)
        self.assertEqual(git_url, clone_url)

    def test_with_user_with_pw(self):
        git_url = "https://github.com/BurntSushi/ripgrep"
        git_user = "user"
        git_pw = "password"
        clone_url = repos.auth_info2clone_url(git_url, git_user, git_pw)
        self.assertEqual(
            "https://user:password@github.com/BurntSushi/ripgrep", clone_url
        )


class TestCloneRepo(unittest.TestCase):
    repo_path = "./test/test_nfs/repos/101-ripgrep"

    def setUp(self):
        os.environ["MOUNT"] = "../test/test_nfs"

    def test_run(self):
        clone_url = "https://github.com/BurntSushi/ripgrep"
        repos.clone_repo(clone_url, self.repo_path)
        self.assertTrue(os.path.exists(self.repo_path))

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.repo_path])


class TestUpdateRepo(unittest.TestCase):
    repo_path = "./test/test_nfs/repos/102-ripgrep"

    def setUp(self):
        subprocess.run(
            ["git", "clone", "https://github.com/BurntSushi/ripgrep", self.repo_path]
        )

    def test_run(self):
        repos.update_repo(self.repo_path)

    def tearDown(self):
        subprocess.run(["rm", "-rf", self.repo_path])


class TestGetRepoPath(unittest.TestCase):
    def test_run(self):
        self.assertTrue(1 == 1)


class TestGetAllCommits(unittest.TestCase):
    def test_run(self):
        self.assertTrue(1 == 1)


class TestGetFilepaths(unittest.TestCase):
    def test_run(self):
        self.assertTrue(1 == 1)


class TestIsParentCommit(unittest.TestCase):
    def test_run(self):
        self.assertTrue(1 == 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
