from typing import Dict

from kubernetes.client import (V1ConfigMap, V1ConfigMapVolumeSource,
                               V1Container, V1EmptyDirVolumeSource, V1EnvVar,
                               V1KeyToPath, V1ObjectMeta, V1Pod,
                               V1PodSecurityContext, V1PodSpec,
                               V1SecretVolumeSource, V1Volume, V1VolumeMount)
from test_orchestrator.settings import config

namespace = config["K8s"]["NAMESPACE"]
adapter_dir = config["Directories"]["adapter_dir"]
adapter_bin = config["Directories"]["adapter_bin"]
adapter_path = adapter_dir + adapter_bin
adapter_url = "http://test-orchestrator.svc.cluster.local/adapter"
sh_string = f"'wget -O {adapter_path} {adapter_url} && chmod +x {adapter_path}'"


def adapter_init_container(adapter_vol):
    return V1Container(
        name="adapter-injector",
        image="gcr.io/google-containers/busybox:latest",
        command=["sh -c"],
        args=[sh_string],
        volume_mounts=[V1VolumeMount(
            name=adapter_vol, mount_path=adapter_dir)
        ]
    )


def build_pod(build_name: str, image_name: str, tar_path: str) -> V1Pod:
    secret_vol = "kaniko-secret"
    tar_vol = "tared-commits"
    context_dir = "/context"

    return V1Pod(
        V1ObjectMeta(name=build_name, namespace=namespace),
        V1PodSpec(
            initContainers=[V1Container(
                name="adapter-injector",
                image="gcr.io/google-containers/busybox:latest",
                command=["wget"],
                args=["-O", "context.tar.gz", tar_path],
                volume_mounts=[V1VolumeMount(
                    name=tar_vol, mount_path=adapter_dir)
                ]
            )],
            containers=[V1Container(
                name=build_name,
                image="gcr.io/kaniko-project/executor:latest",
                args=[f"--context=tar://{context_dir}/context.tar.gz", f"--destination={image_name}",
                      "--cache=True"],
                volume_mounts=[
                    V1VolumeMount(
                        name=secret_vol,
                        mount_path="/kaniko/.docker"
                    ),
                    V1VolumeMount(
                        name=tar_vol,
                        mount_path=context_dir
                    )
                ]
            )],
            volumes=[
                V1Volume(
                    V1SecretVolumeSource(
                        secret_name="regcred",
                        items=V1KeyToPath(
                            path="config.json", key=".dockerconfigjson")
                    ),
                    name=secret_vol
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=tar_vol
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


def one_pod(
        identifier: str,
        image_name: str,
        config_map_name: str,
        config_path: str,
        tester_command: str,
        report_id: str) -> V1Pod:

    config_vol = f"config-{identifier}"
    adapter_vol = f"adapter-{identifier}"

    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod", namespace=namespace),
        V1PodSpec(
            initContainers=[adapter_init_container(adapter_vol)],
            containers=[V1Container(
                name=f"{identifier}-combined",
                image=image_name,
                command=[adapter_path],
                env=[
                    V1EnvVar(name="TESTER_CONFIG", value=tester_command),
                    V1EnvVar(name="REPORT_ID", value=report_id),
                ],
                volume_mounts=[
                    V1VolumeMount(
                        name=config_vol,
                        mount_path=config_path
                    ),
                    V1VolumeMount(
                        name=adapter_vol,
                        mount_path=adapter_dir
                    )
                ]
            )],
            volumes=[
                V1Volume(
                    V1ConfigMapVolumeSource(name=config_map_name),
                    name=config_vol
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=adapter_vol
                )
            ],
            restart_policy="Never",
            # security_context=V1PodSecurityContext(
            #    fs_group=450
            # )
        ),
        kind="Pod",
        api_version="v1"
    )


def two_pod(
        identifier: str,
        app_image_name: str,
        tester_image_name: str,
        config_map_name: str,
        config_path: str,
        tester_command: str,
        report_id: str) -> V1Pod:

    config_vol = f"config-{identifier}"
    adapter_vol = f"adapter-{identifier}"

    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod", namespace=namespace),
        V1PodSpec(
            initContainers=[adapter_init_container(adapter_vol)],
            containers=[
                V1Container(
                    name=f"{identifier}-app",
                    image=app_image_name,
                    volume_mounts=V1VolumeMount(
                        name=config_vol,
                        mount_path=config_path,
                    )
                ),
                V1Container(
                    name=f"{identifier}-tester",
                    image=tester_image_name,
                    command=[adapter_path],
                    env=[
                        V1EnvVar(name="TESTER_CONFIG", value=tester_command),
                        V1EnvVar(name="REPORT_ID", value=report_id),
                    ],
                    volume_mounts=V1VolumeMount(
                        name=adapter_vol,
                        mount_path=adapter_dir
                    )
                )
            ],
            volumes=[
                V1Volume(
                    V1ConfigMapVolumeSource(name=config_map_name),
                    name=config_vol
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=adapter_vol
                )
            ],
            restart_policy="Never",
            # security_context=V1PodSecurityContext(
            #     fs_group=450
            # )
        ),
        kind="Pod",
        api_version="v1"
    )
