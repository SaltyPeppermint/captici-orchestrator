import time

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api

import storage.repositories as repos

NAMESPACE = "nicole-bsc"
NFS_SERVER = "oersted.informatik.uni-leipzig.de"
NFS_TARED_SHARE = "/raid/kube_storage/nicole_bsc/tared_commits"
CONTAINER_REGISTRY_URL = "kube001.informatik.intern.uni-leipzig.de:30005"
CONTAINER_REGISTRY_USER = "cbpb-tester"
KANIKO_SECRET_VOL_NAME = "kaniko-secret"
TARED_COMMITS_VOL_NAME = "tared-commits"


def get_kube_api():
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def craft_manifest(project_name: str, commit_hash: str):
    container_name = f"kaniko-{project_name}-{commit_hash}"
    tar_path_arg = f"--context=tar:///tars/{project_name}/{commit_hash}.tar.gz"
    destination_arg = f"--destination={CONTAINER_REGISTRY_URL}/{CONTAINER_REGISTRY_USER}/{project_name}:{commit_hash}"

    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
                "name": container_name
        },
        "spec": {
            "containers": [{
                "image": "gcr.io/kaniko-project/executor:latest",
                "name": container_name,
                "args": [tar_path_arg, destination_arg],
                "volume_mounts": [
                    {
                        "name": KANIKO_SECRET_VOL_NAME,
                        "mount_path": "/kaniko/.docker"
                    },
                    {
                        "name": TARED_COMMITS_VOL_NAME,
                        "mount_path": "/tars/"
                    }
                ]
            }],
            "restart_policy": "Never",
            "volumes": [
                {
                    "name": KANIKO_SECRET_VOL_NAME,
                    "secret": {
                        "secret_name": "dockercred",
                        "items": [{
                            "key": ".dockerconfigjson",
                            "path": "config.json"
                        }]
                    }
                },
                {
                    "name": TARED_COMMITS_VOL_NAME,
                    "nfs": {
                        "server": NFS_SERVER,
                        "path": NFS_TARED_SHARE,
                        "read_only": True
                    }
                }

            ]
        }
    }
    return pod_manifest


def execute_manifest(api_instance, manifest):
    name = manifest["metadata"]["name"]
    resp = None

    print(f"Creating kaniko build container {name} ...")

    resp = api_instance.create_namespaced_pod(body=manifest,
                                              namespace=NAMESPACE)
    while True:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=NAMESPACE)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)
    print("Done.")


def build_commit(project_name: str, commit_hash: str):
    core_v1 = get_kube_api()
    repos.tar_into(project_name, commit_hash)

    manifest = craft_manifest(project_name, commit_hash)

    execute_manifest(core_v1, manifest)
