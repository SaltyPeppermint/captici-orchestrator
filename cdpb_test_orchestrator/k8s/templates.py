from typing import Dict

from cdpb_test_orchestrator import settings
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


def _orchestrator_url() -> str:
    return "cdpb-test-orchestrator" + settings.namespace() + ".svc.cluster.local:8000"


def _config_map_name(test_id: int) -> str:
    return f"config-map-{test_id}"


def config_map(test_id: int, config_dict: Dict[str, str]) -> V1ConfigMap:
    return V1ConfigMap(
        metadata=V1ObjectMeta(
            name=_config_map_name(test_id), namespace=settings.namespace()
        ),
        data=config_dict,
        kind="ConfigMap",
        api_version="v1",
    )


def build_job(
    build_id: str, image_name: str, tar_path: str, dockerfile_path: str
) -> V1Job:
    tar_vol_name = f"tar-vol-{build_id}"
    context_dir = "/context"
    init_container = [
        V1Container(
            name=f"tar-downloader-{build_id}",
            image="gcr.io/google-containers/busybox:latest",
            command=["wget"],
            args=[
                "-O",
                f"{context_dir}/context.tar.gz",
                f"{_orchestrator_url()}/internal/tars?tar_path={tar_path}",
            ],
            volume_mounts=[V1VolumeMount(name=tar_vol_name, mount_path=context_dir)],
        )
    ]

    regcred_vol_name = f"regcred-vol-{build_id}"
    container = [
        V1Container(
            name=f"kaniko-{build_id}",
            image="gcr.io/kaniko-project/executor:latest",
            args=[
                f"--context=tar:///{context_dir}/context.tar.gz",
                f"--destination={image_name}",
                f"--dockerfile={dockerfile_path}",
                "--cache=True",
            ],
            volume_mounts=[
                V1VolumeMount(name=regcred_vol_name, mount_path="/kaniko/.docker"),
                V1VolumeMount(name=tar_vol_name, mount_path=context_dir),
            ],
        )
    ]

    volumes = [
        V1Volume(
            secret=V1SecretVolumeSource(
                secret_name="regcred",
                items=[V1KeyToPath(path="config.json", key=".dockerconfigjson")],
            ),
            name=regcred_vol_name,
        ),
        V1Volume(
            empty_dir=V1EmptyDirVolumeSource(medium="Memory"),
            name=tar_vol_name,
        ),
    ]

    job_spec = V1JobSpec(
        ttl_seconds_after_finished=30,
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                name=f"build-pod-{build_id}", namespace=settings.namespace()
            ),
            spec=V1PodSpec(
                init_containers=init_container,
                containers=container,
                volumes=volumes,
                restart_policy="Never",
            ),
        ),
    )

    return V1Job(
        kind="Job",
        api_version="batch/v1",
        metadata=V1ObjectMeta(
            name=f"build-job-{build_id}", namespace=settings.namespace()
        ),
        spec=job_spec,
    )


def test_job(
    test_id: int,
    app_image_name: str,
    config_folder: str,
    tester_command: str,
    result_path: str,
    threshold: float,
    tester_image_name: str | None = None,
) -> V1Job:
    adapter_dir = "/opt"
    adapter_path = adapter_dir + "/adapter"
    adapter_vol_name = f"adapter-vol-{test_id}"
    init_containers = [
        V1Container(
            name=f"adapter-injector-{test_id}",
            image="gcr.io/google-containers/busybox:latest",
            command=["sh -c"],
            args=[
                f"wget -O {adapter_path} {_orchestrator_url()}/internal/adapter",
                f"chmod +x {adapter_path}",
            ],
            volume_mounts=[
                V1VolumeMount(name=adapter_vol_name, mount_path=adapter_dir)
            ],
        )
    ]

    config_vol_name = f"config-vol-{test_id}"
    env = [
        V1EnvVar(name="TESTER_COMMAND", value=tester_command),
        V1EnvVar(name="THRESHOLD", value=str(threshold)),
        V1EnvVar(name="RESULT_PATH", value=result_path),
    ]
    if tester_image_name:
        containers = [
            V1Container(
                name=f"app-{test_id}",
                image=app_image_name,
                volume_mounts=[
                    V1VolumeMount(name=config_vol_name, mount_path=config_folder)
                ],
            ),
            V1Container(
                name=f"tester-{test_id}",
                image=tester_image_name,
                command=[adapter_path],
                env=env,
                volume_mounts=[
                    V1VolumeMount(name=adapter_vol_name, mount_path=adapter_dir)
                ],
            ),
        ]
    else:
        containers = [
            V1Container(
                name=f"combined-{test_id}",
                image=app_image_name,
                command=[adapter_path],
                env=env,
                volume_mounts=[
                    V1VolumeMount(name=config_vol_name, mount_path=config_folder),
                    V1VolumeMount(name=adapter_vol_name, mount_path=adapter_dir),
                ],
            )
        ]

    volumes = [
        V1Volume(
            config_map=V1ConfigMapVolumeSource(name=_config_map_name(test_id)),
            name=config_vol_name,
        ),
        V1Volume(
            empty_dir=V1EmptyDirVolumeSource(medium="Memory"),
            name=adapter_vol_name,
        ),
    ]

    job_spec = V1JobSpec(
        ttl_seconds_after_finished=30,
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                name=f"test-pod-{test_id}", namespace=settings.namespace()
            ),
            spec=V1PodSpec(
                init_containers=init_containers,
                containers=containers,
                volumes=volumes,
                restart_policy="Never",
            ),
        ),
    )

    return V1Job(
        kind="Pod",
        api_version="batch/v1",
        metadata=V1ObjectMeta(
            name=f"test-job-{test_id}", namespace=settings.namespace()
        ),
        spec=job_spec,
    )
