from typing import Dict, List, Optional

from cdpb_test_orchestrator.settings import get_config
from kubernetes.client import (
    V1ConfigMap,
    V1ConfigMapVolumeSource,
    V1Container,
    V1EmptyDirVolumeSource,
    V1EnvVar,
    V1Job,
    V1JobSpec,
    V1KeyToPath,
    V1ObjectMeta,
    V1PodSpec,
    V1PodTemplateSpec,
    V1SecretVolumeSource,
    V1Volume,
    V1VolumeMount,
)


def get_adapter_dir() -> str:
    config = get_config()
    adapter_dir = config["Directories"]["adapter_dir"]
    return adapter_dir


def get_adapter_path() -> str:
    config = get_config()
    adapter_dir = get_adapter_dir()
    adapter_bin = config["Directories"]["adapter_bin"]
    adapter_path = adapter_dir + adapter_bin
    return adapter_path


def get_orchestrator_url() -> str:
    return "cdpb-test-orchestrator.cdpb-tester.svc.cluster.local:8000"


def get_sh_cmd() -> str:
    adapter_path = get_adapter_path()
    adapter_url = get_orchestrator_url() + "/internal/adapter"
    return f"'wget -O {adapter_path} {adapter_url} && chmod +x {adapter_path}'"


def get_tar_download_cmd(tar_path: str) -> str:
    return get_orchestrator_url() + "/internal/tars?tar_path=" + tar_path


def config_map(test_id: int, config_dict: Dict[str, str]):
    return V1ConfigMap(
        metadata=V1ObjectMeta(name=config_map_name(test_id)),
        data=config_dict,
        kind="ConfigMap",
        api_version="v1",
    )


def build_job(
    build_id: str, image_name: str, tar_path: str, dockerfile_path: str
) -> V1Job:
    config = get_config()
    regcred_vol_name = f"regcred-vol-{build_id}"
    tar_vol_name = f"tar-vol-{build_id}"
    context_dir = "/context"
    args = [
        f"--context=tar:///{context_dir}/context.tar.gz",
        f"--destination={image_name}",
        f"--dockerfile={dockerfile_path}",
        "--cache=True",
    ]
    job_spec = V1JobSpec(
        ttl_seconds_after_finished=30,
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                name=f"build-pod-{build_id}", namespace=config["K8s"]["NAMESPACE"]
            ),
            spec=V1PodSpec(
                init_containers=build_pod_init_container(
                    build_id, tar_path, tar_vol_name, context_dir
                ),
                containers=build_pod_container(
                    build_id, regcred_vol_name, tar_vol_name, context_dir, args
                ),
                volumes=build_pod_volumes(regcred_vol_name, tar_vol_name),
                restart_policy="Never",
            ),
        ),
    )

    job = V1Job(
        kind="Job",
        api_version="batch/v1",
        metadata=V1ObjectMeta(
            name=f"build-job-{build_id}", namespace=config["K8s"]["NAMESPACE"]
        ),
        spec=job_spec,
    )
    return job


def build_pod_volumes(regcred_vol_name, tar_vol_name):
    return [
        V1Volume(
            secret=V1SecretVolumeSource(
                secret_name="regcred",
                items=[V1KeyToPath(path="config.json", key=".dockerconfigjson")],
            ),
            name=regcred_vol_name,
        ),
        V1Volume(empty_dir=V1EmptyDirVolumeSource(medium="Memory"), name=tar_vol_name),
    ]


def build_pod_container(build_id, regcred_vol_name, tar_vol_name, context_dir, args):
    return [
        V1Container(
            name=f"kaniko-{build_id}",
            image="gcr.io/kaniko-project/executor:latest",
            args=args,
            volume_mounts=[
                V1VolumeMount(name=regcred_vol_name, mount_path="/kaniko/.docker"),
                V1VolumeMount(name=tar_vol_name, mount_path=context_dir),
            ],
        )
    ]


def build_pod_init_container(build_id, tar_path, tar_vol_name, context_dir):
    return [
        V1Container(
            name=f"context-downloader-{build_id}",
            image="gcr.io/google-containers/busybox:latest",
            command=["wget"],
            args=[
                "-O",
                f"{context_dir}/context.tar.gz",
                get_tar_download_cmd(tar_path),
            ],
            volume_mounts=[V1VolumeMount(name=tar_vol_name, mount_path=context_dir)],
        )
    ]


def test_job(
    test_id: int,
    app_image_name: str,
    config_folder: str,
    tester_command: str,
    result_path: str,
    threshold: float,
    tester_image_name: str | None = None,
) -> V1Job:
    config = get_config()
    env = test_pod_env(tester_command, threshold, result_path)
    job_spec = V1JobSpec(
        ttl_seconds_after_finished=30,
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                name=f"test-pod-{test_id}", namespace=config["K8s"]["NAMESPACE"]
            ),
            spec=V1PodSpec(
                init_containers=[test_pod_init_container(test_id)],
                containers=test_pod_container(
                    test_id, app_image_name, config_folder, env, tester_image_name
                ),
                volumes=test_pod_volumes(test_id),
                restart_policy="Never",
            ),
        ),
    )
    return V1Job(
        kind="Pod",
        api_version="batch/v1",
        metadata=V1ObjectMeta(
            name=f"test-job-{test_id}", namespace=config["K8s"]["NAMESPACE"]
        ),
        spec=job_spec,
    )


def test_pod_init_container(test_id: int):
    return V1Container(
        name=f"adapter-injector-{test_id}",
        image="gcr.io/google-containers/busybox:latest",
        command=["sh -c"],
        args=[get_sh_cmd()],
        volume_mounts=[
            V1VolumeMount(name=adapter_vol_name(test_id), mount_path=get_adapter_dir())
        ],
    )


def test_pod_volumes(test_id):
    return [
        V1Volume(
            config_map=V1ConfigMapVolumeSource(name=config_map_name(test_id)),
            name=config_vol_name(test_id),
        ),
        V1Volume(
            empty_dir=V1EmptyDirVolumeSource(medium="Memory"),
            name=adapter_vol_name(test_id),
        ),
    ]


def test_pod_container(
    test_id: int,
    app_image_name: str,
    config_folder: str,
    env: List[V1EnvVar],
    tester_image_name: Optional[str],
) -> List[V1Container]:
    adapter_path = get_adapter_path()
    adapter_dir = get_adapter_dir()
    if tester_image_name:
        container_list = [
            V1Container(
                name=f"app-{test_id}",
                image=app_image_name,
                volume_mounts=[
                    V1VolumeMount(
                        name=config_vol_name(test_id), mount_path=config_folder
                    )
                ],
            ),
            V1Container(
                name=f"tester-{test_id}",
                image=tester_image_name,
                command=[get_adapter_path()],
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
                name=f"combined-{test_id}",
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


def test_pod_env(tester_command: str, threshold: float, result_path: str):
    return [
        V1EnvVar(name="TESTER_COMMAND", value=tester_command),
        V1EnvVar(name="THRESHOLD", value=str(threshold)),
        V1EnvVar(name="RESULT_PATH", value=result_path),
    ]


def adapter_vol_name(test_id: int) -> str:
    return f"adapter-vol-{test_id}"


def config_vol_name(test_id: int) -> str:
    return f"config-vol-{test_id}"


def config_map_name(test_id: int) -> str:
    return f"config-map-{test_id}"
