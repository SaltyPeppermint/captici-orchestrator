from typing import Dict, List, Optional

from kubernetes.client import (
    V1ConfigMap,
    V1ConfigMapVolumeSource,
    V1Container,
    V1EmptyDirVolumeSource,
    V1EnvVar,
    V1KeyToPath,
    V1ObjectMeta,
    V1Pod,
    V1PodSecurityContext,
    V1PodSpec,
    V1SecretVolumeSource,
    V1Volume,
    V1VolumeMount,
)
from test_orchestrator.settings import config

namespace = config["K8s"]["NAMESPACE"]
adapter_dir = config["Directories"]["adapter_dir"]
adapter_bin = config["Directories"]["adapter_bin"]
adapter_path = adapter_dir + adapter_bin
adapter_url = "http://test-orachestrator.svc.cluster.local/internal/adapter"
sh_cmd = f"'wget -O {adapter_path} {adapter_url} && chmod +x {adapter_path}'"


def pod_builder_pod(project_id: int, image_name: str, tar_path: str) -> V1Pod:
    regcred_vol_name = f"{project_id}-RegcredVol"
    tar_vol_name = f"{project_id}-TarVol"
    context_dir = "/context"
    args = [
        f"--context=tar://{context_dir}/context.tar.gz",
        f"--destination={image_name}",
        "--cache=True",
    ]
    return V1Pod(
        V1ObjectMeta(name=f"{project_id}-BuildPod", namespace=namespace),
        V1PodSpec(
            init_containers=[
                V1Container(
                    name="adapter-injector",
                    image="gcr.io/google-containers/busybox:latest",
                    command=["wget"],
                    args=["-O", "context.tar.gz", tar_path],
                    volume_mounts=[
                        V1VolumeMount(name=tar_vol_name, mount_path=adapter_dir)
                    ],
                )
            ],
            containers=[
                V1Container(
                    name=f"{project_id}-Kaniko",
                    image="gcr.io/kaniko-project/executor:latest",
                    args=args,
                    volume_mounts=[
                        V1VolumeMount(
                            name=regcred_vol_name, mount_path="/kaniko/.docker"
                        ),
                        V1VolumeMount(name=tar_vol_name, mount_path=context_dir),
                    ],
                )
            ],
            volumes=[
                V1Volume(
                    V1SecretVolumeSource(
                        secret_name="regcred",
                        items=V1KeyToPath(path="config.json", key=".dockerconfigjson"),
                    ),
                    name=regcred_vol_name,
                ),
                V1Volume(V1EmptyDirVolumeSource(medium="Memory"), name=tar_vol_name),
            ],
            restart_policy="Never",
            security_context=V1PodSecurityContext(fs_group=450),
        ),
    )


def adapter_init_container(test_id: int):
    return V1Container(
        name=f"{test_id}-AdapterInjector",
        image="gcr.io/google-containers/busybox:latest",
        command=["sh -c"],
        args=[sh_cmd],
        volume_mounts=[
            V1VolumeMount(name=adapter_vol_name(test_id), mount_path=adapter_dir)
        ],
    )


def config_map(test_id: int, config_dict: Dict[str, str]):
    return V1ConfigMap(
        metadata=V1ObjectMeta(name=config_map_name(test_id)),
        data=config_dict,
        kind="ConfigMap",
        api_version="v1",
    )


def pod(
    test_id: int,
    app_image_name: str,
    config_folder: str,
    tester_command: str,
    result_path: str,
    threshold: float,
    tester_image_name: str | None = None,
) -> V1Pod:
    env = pod_env(tester_command, threshold, result_path)
    return V1Pod(
        metadata=V1ObjectMeta(name=pod_name(test_id), namespace=namespace),
        spec=V1PodSpec(
            init_containers=[adapter_init_container(test_id)],
            containers=pod_container(
                test_id, app_image_name, config_folder, env, tester_image_name
            ),
            volumes=[
                V1Volume(
                    V1ConfigMapVolumeSource(name=config_map_name(test_id)),
                    name=config_vol_name(test_id),
                ),
                V1Volume(
                    V1EmptyDirVolumeSource(medium="Memory"),
                    name=adapter_vol_name(test_id),
                ),
            ],
            restart_policy="Never",
            # security_context=V1PodSecurityContext(
            #    fs_group=450
            # )
        ),
        kind="Pod",
        api_version="v1",
    )


def pod_container(
    test_id: int,
    app_image_name: str,
    config_folder: str,
    env: List[V1EnvVar],
    tester_image_name: Optional[str],
) -> List[V1Container]:
    if tester_image_name:
        container_list = [
            V1Container(
                name=f"{test_id}-App",
                image=app_image_name,
                volume_mounts=[
                    V1VolumeMount(
                        name=config_vol_name(test_id), mount_path=config_folder
                    )
                ],
            ),
            V1Container(
                name=f"{test_id}-Tester",
                image=tester_image_name,
                command=[adapter_path],
                env=env,
                volume_mounts=[
                    V1VolumeMount(
                        name=adapter_vol_name(test_id), mount_path=adapter_dir
                    )
                ],
            ),
        ]
    else:
        container_list = [
            V1Container(
                name=f"{test_id}-Combined",
                image=app_image_name,
                command=[adapter_path],
                env=env,
                volume_mounts=[
                    V1VolumeMount(
                        name=config_vol_name(test_id), mount_path=config_folder
                    ),
                    V1VolumeMount(
                        name=adapter_vol_name(test_id), mount_path=adapter_dir
                    ),
                ],
            )
        ]
    return container_list


def pod_env(tester_command: str, threshold: float, result_path: str):
    return [
        V1EnvVar(name="TESTER_COMMAND", value=tester_command),
        V1EnvVar(name="THRESHOLD", value=str(threshold)),
        V1EnvVar(name="RESULT_PATH", value=result_path),
    ]


def pod_name(test_id: int) -> str:
    return f"{test_id}-Pod"


def adapter_vol_name(test_id: int) -> str:
    return f"{test_id}-AdapterVol"


def config_vol_name(test_id: int) -> str:
    return f"{test_id}-ConfigVol"


def config_map_name(test_id: int) -> str:
    return f"{test_id}-ConfigMap"
