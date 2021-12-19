import unittest

from cdpb_test_orchestrator.k8s import build_commit


class TestK8sApi(unittest.TestCase):
    def test_build_commit(self):
        tar_path = (
            "/var/nfs/tars/1-ripgrep/0b36942f680bfa9ae88a564f2636aa8286470073.tar.gz"
        )
        project_id = 2
        commit_hash = "0b36942f680bfa9ae88a564f2636aa8286470073"
        build_commit(tar_path, project_id, commit_hash)
