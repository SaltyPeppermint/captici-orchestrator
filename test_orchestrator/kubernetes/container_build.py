from settings import *

import k8s_api
import storage.repositories as repos


def build_commit(project_name: str, commit_hash: str):
    repos.tar_into(project_name, commit_hash)

    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
                "name": f"kaniko-{project_name}-{commit_hash}"
        },
        "spec": {
            "containers": [{
                "image": "gcr.io/kaniko-project/executor:latest",
                "name": f"kaniko-{project_name}-{commit_hash}",
                "args": [
                    f"--context=tar:///tared_commits/{project_name}/{commit_hash}.tar.gz",
                    f"--destination={CONTAINER_REGISTRY_URL}/{CONTAINER_REGISTRY_USER}/{project_name}:{commit_hash}",
                    "--cache=True",
                    "--skip-tls-verify-registry"
                ],
                "volume_mounts": [
                    {
                        "name": KANIKO_SECRET_VOL_NAME,
                        "mount_path": "/kaniko/.docker"
                    },
                    {
                        "name": TARED_COMMITS_VOL_NAME,
                        "mount_path": "/tared_commits"
                    }
                ]
            }],
            "security_context": {
                "fs_group": 450
            },
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

    k8s_api.execute_manifest(pod_manifest)
    return
