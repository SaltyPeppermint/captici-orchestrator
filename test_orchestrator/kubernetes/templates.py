from typing import Dict
from ..settings import *
from kubernetes.client import V1ConfigMap, V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1Volume, V1VolumeMount, V1SecretVolumeSource, V1NFSVolumeSource, V1KeyToPath, V1PodSecurityContext, V1EnvVar, V1EmptyDirVolumeSource, V1ConfigMapVolumeSource


KANIKO_SECRET_VOL_NAME = "kaniko-secret"
TARED_COMMITS_VOL_NAME = "tared-commits"
TEST_REPORT_VOL_NAME = "test-reports"
ADAPTER_SHARED_VOL_NAME = "adapter-download"
ADAPTER_DOWNLOAD_FOLDER = "/downloads"
APP_CONFIG_MAP_VOL_NAME = "app-config"


def build_pod(build_name: str, image_name: str, tar_path: str) -> V1Pod:
    return V1Pod(
        V1ObjectMeta(name=build_name),
        V1PodSpec(
            containers=[V1Container(
                name=build_name,
                image="gcr.io/kaniko-project/executor:latest",
                args=["--context=tar://{tar_path}", "--destination={image_name}",
                      "--cache=True", "--skip-tls-verify-registry"],
                volume_mounts=[
                    V1VolumeMount(
                        name=KANIKO_SECRET_VOL_NAME,
                        mount_path="/kaniko/.docker"
                    ),
                    V1VolumeMount(
                        name=TARED_COMMITS_VOL_NAME,
                        mount_path="/tars"
                    )
                ]

            )],
            volumes=[
                V1Volume(
                    V1SecretVolumeSource(
                        secret_name="dockercred",
                        items=V1KeyToPath(
                            path=".dockerconfigjson", key="config.json")
                    ),
                    name=KANIKO_SECRET_VOL_NAME
                ),
                V1Volume(
                    V1NFSVolumeSource(
                        server=NFS_SERVER,
                        path=NFS_TARED_SHARE,
                        read_only=True
                    ),
                    name=TARED_COMMITS_VOL_NAME
                )
            ],
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        )
    )


def config_map(config_name: str, config_data: Dict[str, str]):
    return V1ConfigMap(
        V1ObjectMeta(name=config_name),
        data=config_data,
        kind="ConfigMap",
        api_version="v1",
    )


def one_pod(identifier: str, image_name: str, app_config_map_name: str, app_config_mount: str, tester_env: str) -> V1Pod:
    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod"),
        V1PodSpec(
            initContainers=[V1Container(
                name="adapter-injector",
                image="gcr.io/google-containers/busybox:latest",
                command=["wget"],
                args=["-O", f"{ADAPTER_DOWNLOAD_FOLDER}/performance-test-adapter", "http://test-orchestrator.svc.cluster.local/performance-test-adapter",
                      "&&", "chmod +x", "/downloads/performance-test-adapter"],
                volume_mounts=[
                    V1VolumeMount(
                        name=ADAPTER_SHARED_VOL_NAME,
                        mount_path=ADAPTER_DOWNLOAD_FOLDER
                    )
                ]
            )],
            containers=[V1Container(
                name=f"{identifier}-combined",
                image=image_name,
                command=[f"{ADAPTER_DOWNLOAD_FOLDER}/adapter"],
                env=[
                    V1EnvVar(name="TESTER_CONFIG", value=tester_env),
                ],
                volume_mounts=[
                    V1VolumeMount(
                        name=TEST_REPORT_VOL_NAME,
                        mount_path="/reports"
                    ),
                    V1VolumeMount(
                        name=APP_CONFIG_MAP_VOL_NAME,
                        mount_path=app_config_mount
                    ),
                    V1VolumeMount(
                        name=ADAPTER_SHARED_VOL_NAME,
                        mount_path=ADAPTER_DOWNLOAD_FOLDER
                    )
                ]
            )],
            volumes=[
                V1Volume(
                    V1NFSVolumeSource(
                        server=NFS_SERVER,
                        path=NFS_REPORT_SHARE,
                        read_only=False
                    ),
                    name=TEST_REPORT_VOL_NAME
                ),
                V1Volume(
                    V1ConfigMapVolumeSource(name=app_config_map_name),
                    name=APP_CONFIG_MAP_VOL_NAME
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=ADAPTER_SHARED_VOL_NAME
                )
            ],
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        ),
        kind="Pod",
        api_version="v1"
    )


def one_pod(identifier: str, app_image_name: str, tester_image_name: str, app_config_map_name: str, app_config_mount: str, tester_env: str) -> V1Pod:
    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod"),
        V1PodSpec(
            initContainers=[V1Container(
                name="adapter-injector",
                image="gcr.io/google-containers/busybox:latest",
                command=["wget"],
                args=["-O", f"{ADAPTER_DOWNLOAD_FOLDER}/performance-test-adapter", "http://test-orchestrator.svc.cluster.local/performance-test-adapter",
                      "&&", "chmod +x", "/downloads/performance-test-adapter"],
                volume_mounts=[
                    V1VolumeMount(
                        name=ADAPTER_SHARED_VOL_NAME,
                        mount_path=ADAPTER_DOWNLOAD_FOLDER
                    )
                ]
            )],
            containers=[
                V1Container(
                    name=f"{identifier}-app",
                    image=app_image_name,
                    volume_mounts=[
                        V1VolumeMount(
                            name=APP_CONFIG_MAP_VOL_NAME,
                            mount_path=app_config_mount,
                        )
                    ]
                ),
                V1Container(
                    name=f"{identifier}-tester",
                    image=tester_image_name,
                    command=[f"{ADAPTER_DOWNLOAD_FOLDER}/adapter"],
                    env=[
                        V1EnvVar(name="TESTER_CONFIG", value=tester_env),
                    ],
                    volume_mounts=[
                        V1VolumeMount(
                            name=TEST_REPORT_VOL_NAME,
                            mount_path="/reports"
                        ),
                        V1VolumeMount(
                            name=ADAPTER_SHARED_VOL_NAME,
                            mount_path=ADAPTER_DOWNLOAD_FOLDER
                        )
                    ]
                )
            ],
            volumes=[
                V1Volume(
                    V1NFSVolumeSource(
                        server=NFS_SERVER,
                        path=NFS_REPORT_SHARE,
                        read_only=False
                    ),
                    name=TEST_REPORT_VOL_NAME
                ),
                V1Volume(
                    V1ConfigMapVolumeSource(name=app_config_map_name),
                    name=APP_CONFIG_MAP_VOL_NAME
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=ADAPTER_SHARED_VOL_NAME
                )
            ],
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        ),
        kind="Pod",
        api_version="v1"
    )
