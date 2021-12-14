from typing import Dict
from kubernetes.client import V1ConfigMap, V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1Volume, V1VolumeMount, V1SecretVolumeSource, V1KeyToPath, V1PodSecurityContext, V1EnvVar, V1EmptyDirVolumeSource, V1ConfigMapVolumeSource

from test_orchestrator.settings import config

namespace = config["K8s"]["NAMESPACE"]
adapter_dir = config["Directories"]["adapter_dir"]
adapter_bin = config["Directories"]["adapter_bin"]
download_string = f"'wget -O {adapter_dir + adapter_bin} http://test-orchestrator.svc.cluster.local/adapter && chmod +x {adapter_dir + adapter_bin}'"


def adapter_init_container(adapter_vol):
    return V1Container(
        name="adapter-injector",
        image="gcr.io/google-containers/busybox:latest",
        command=["sh -c"],
        args=[download_string],
        volume_mounts=[V1VolumeMount(
            name=adapter_vol, mount_path=adapter_dir)
        ]
    )


def kaniko_init_container(tar_vol, tar_path):
    return V1Container(
        name="adapter-injector",
        image="gcr.io/google-containers/busybox:latest",
        command=["wget"],
        args=["-O", "context.tar.gz", tar_path],
        volume_mounts=[V1VolumeMount(
            name=tar_vol, mount_path=adapter_dir)
        ]
    )


def build_pod(build_name: str, image_name: str, tar_path: str) -> V1Pod:
    secret_vol = "kaniko-secret"
    tar_vol = "tared-commits"
    context_dir = "/context"

    return V1Pod(
        V1ObjectMeta(name=build_name, namespace=namespace),
        V1PodSpec(
            initContainers=[kaniko_init_container(tar_vol, tar_path)],
            containers=[V1Container(
                name=build_name,
                image="gcr.io/kaniko-project/executor:latest",
                args=[f"--context=tar://{context_dir}/context.tar.gz", f"--destination={image_name}",
                      "--cache=True"],
                volume_mounts=kaniko_mounts(secret_vol, tar_vol, context_dir)

            )],
            volumes=kaniko_volumes(secret_vol, tar_vol),
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        )
    )


def kaniko_mounts(secret_volume, tar_vol, context_dir):
    return [
        V1VolumeMount(
            name=secret_volume,
            mount_path="/kaniko/.docker"
        ),
        V1VolumeMount(
            name=tar_vol,
            mount_path=context_dir
        )
    ]


def kaniko_volumes(secret_volume, tar_vol):
    return [
        V1Volume(
            V1SecretVolumeSource(
                secret_name="regcred",
                items=V1KeyToPath(
                            path="config.json", key=".dockerconfigjson")
            ),
            name=secret_volume
        ),
        V1Volume(
            V1EmptyDirVolumeSource(medium="Memory"),
            name=tar_vol
        )
    ]


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
        app_config_map_name: str,
        app_config_path: str,
        tester_env: str,
        report_id: str) -> V1Pod:

    app_config_vol = f"{identifier}-app-config"
    adapter_vol = f"{identifier}-adapter"
    report_vol = f"{identifier}-reports"

    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod", namespace=namespace),
        V1PodSpec(
            initContainers=[adapter_init_container(adapter_vol)],
            containers=[V1Container(
                name=f"{identifier}-combined",
                image=image_name,
                command=[adapter_dir + adapter_bin],
                env=[
                    V1EnvVar(name="TESTER_CONFIG", value=tester_env),
                    V1EnvVar(name="REPORT_ID", value=report_id),
                ],
                volume_mounts=one_pod_mounts(
                    app_config_path,
                    app_config_vol,
                    adapter_vol,
                    report_vol
                )
            )],
            volumes=one_pod_volumes(
                app_config_map_name,
                app_config_vol,
                adapter_vol,
                report_vol
            ),
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        ),
        kind="Pod",
        api_version="v1"
    )


def one_pod_volumes(app_config_map_name, app_config_vol, adapter_vol):
    return [
        V1Volume(
            V1ConfigMapVolumeSource(name=app_config_map_name),
            name=app_config_vol
        ),
        V1Volume(
            V1EmptyDirVolumeSource(medium="Memory"),
            name=adapter_vol
        )
    ]


def one_pod_mounts(app_config_mount, app_config_vol, adapter_vol):
    return [
        V1VolumeMount(
            name=app_config_vol,
            mount_path=app_config_mount
        ),
        V1VolumeMount(
            name=adapter_vol,
            mount_path=adapter_dir
        )
    ]


def two_pod(
        identifier: str,
        app_image_name: str,
        tester_image_name: str,
        app_config_map_name: str,
        app_config_path: str,
        tester_env: str,
        report_id: str) -> V1Pod:

    app_config_vol = f"{identifier}-app-config"
    adapter_vol = f"{identifier}-adapter"
    report_vol = f"{identifier}-reports"

    return V1Pod(
        V1ObjectMeta(name=f"{identifier}-pod", namespace=namespace),
        V1PodSpec(
            initContainers=[adapter_init_container(adapter_vol)],
            containers=[
                V1Container(
                    name=f"{identifier}-app",
                    image=app_image_name,
                    volume_mounts=two_pod_app_mounts(
                        app_config_path,
                        app_config_vol
                    )
                ),
                V1Container(
                    name=f"{identifier}-tester",
                    image=tester_image_name,
                    command=[adapter_dir + adapter_bin],
                    env=[
                        V1EnvVar(name="TESTER_CONFIG", value=tester_env),
                        V1EnvVar(name="REPORT_ID", value=report_id),
                    ],
                    volume_mounts=two_pod_tester_mounts(
                        adapter_vol,
                        report_vol
                    )
                )
            ],
            volumes=two_pod_volumes(
                app_config_map_name, app_config_vol, adapter_vol),
            restart_policy="Never",
            security_context=V1PodSecurityContext(
                fs_group=450
            )
        ),
        kind="Pod",
        api_version="v1"
    )


def two_pod_app_mounts(app_config_mount, app_config_vol):
    return [
        V1VolumeMount(
            name=app_config_vol,
            mount_path=app_config_mount,
        )
    ]


def two_pod_tester_mounts(adapter_vol):
    return [
        V1VolumeMount(
            name=adapter_vol,
            mount_path=adapter_dir
        )
    ]


def two_pod_volumes(app_config_map_name, app_config_vol, adapter_vol):
    return [
        V1Volume(
            V1ConfigMapVolumeSource(name=app_config_map_name),
            name=app_config_vol
        ),
        V1Volume(
            V1EmptyDirVolumeSource(medium="Memory"),
            name=adapter_vol
        )
    ]
