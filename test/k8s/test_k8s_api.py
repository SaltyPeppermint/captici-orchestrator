import unittest

from cdpb_test_orchestrator.k8s import build_commit


class TestK8sApi(unittest.TestCase):
    def test_build_commit(self):
        tar_path = (
            "/var/nfs/tars/1-demo/3ff73097efa92d32a19b09ec3ea113042d637ca2.tar.gz"
        )
        project_id = 1
        commit_hash = "3ff73097efa92d32a19b09ec3ea113042d637ca2"
        dockerfile_path = "./Dockerfile"
        build_commit(tar_path, project_id, commit_hash, dockerfile_path)
