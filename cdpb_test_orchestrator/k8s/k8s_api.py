import logging
from typing import Dict, List

from cdpb_test_orchestrator import settings
from cdpb_test_orchestrator.data_objects import Project
from kubernetes import config, watch
from kubernetes.client.api.batch_v1_api import BatchV1Api
from kubernetes.client.api.core_v1_api import CoreV1Api
from kubernetes.client.configuration import Configuration
from kubernetes.client.models.v1_config_map import V1ConfigMap
from kubernetes.client.models.v1_job import V1Job

from . import templates

logger = logging.getLogger("uvicorn")


def _load_credentials() -> None:
    if settings.is_debug():
        config.load_kube_config()
        try:
            c = Configuration().get_default_copy()
        except AttributeError:
            c = Configuration()
            c.assert_hostname = False
        Configuration.set_default(c)
    else:
        config.load_incluster_config()
    return


def _get_core_api() -> CoreV1Api:
    _load_credentials()
    core_v1 = CoreV1Api()
    return core_v1


def _get_batch_api() -> BatchV1Api:
    _load_credentials()
    batch_v1 = BatchV1Api()
    return batch_v1


def _await_build_jobs(api: BatchV1Api, namespace: str, manifests: List[V1Job]) -> None:
    names = [manifest.metadata.name for manifest in manifests]
    w = watch.Watch()
    for event in w.stream(api.list_namespaced_job, namespace=namespace):
        logger.info(
            f"Build Job: {event['object'].metadata.name} "
            f"{event['object'].status.succeeded} succeeded."
        )
        if event["object"].metadata.name in names:
            if event["object"].status.succeeded == 1:
                logger.info(f"{event['object'].metadata.name} finished.")
                names.remove(event["object"].metadata.name)
        if names == []:
            w.stop()
            break
    return


def build_commit(tar_path: str, project: Project, commit_hash: str) -> str:
    api = _get_batch_api()
    namespace = settings.namespace()
    image_name = (
        f"{settings.reg_url()}/{settings.reg_user()}/{project.id}:{commit_hash}"
    )
    build_id = f"{project.id}-{commit_hash}"

    manifest = templates.build_job(
        build_id, image_name, tar_path, project.dockerfile_path
    )
    api.create_namespaced_job(body=manifest, namespace=namespace)

    _await_build_jobs(api, namespace, [manifest])
    return image_name


def build_commits(
    project_id: int,
    project: Project,
    tar_paths: Dict[str, str],
) -> Dict[str, str]:
    api = _get_batch_api()
    namespace = settings.namespace()

    app_image_names = {}
    manifests = []
    for commit_hash, tar_path in tar_paths.items():
        image_name = (
            f"{settings.reg_url()}/{settings.reg_user()}/{project_id}:{commit_hash}"
        )
        build_id = f"{project_id}-{commit_hash}"
        manifest = templates.build_job(
            build_id, image_name, tar_path, project.dockerfile_path
        )
        api.create_namespaced_job(body=manifest, namespace=namespace)
        manifests.append(manifest)
        app_image_names[commit_hash] = image_name

    logger.info(
        f"Built images of commits {tar_paths} for initial test of {project_id}."
    )
    for manifest in manifests:
        _await_build_jobs(api, namespace, manifests)

    return app_image_names


def _execute_config_map(manifest: V1ConfigMap) -> None:
    api = _get_core_api()
    name = manifest.metadata.name
    namespace = settings.namespace()
    api.create_namespaced_config_map(body=manifest, namespace=namespace)

    w = watch.Watch()
    for event in w.stream(api.list_namespaced_config_map, namespace=namespace):
        logger.info(f"ConfigMap: {event['object'].metadata.name} {event['type']}")
        if event["object"].metadata.name == name:
            if event["type"] == "ADDED":
                w.stop()
                logger.info(f"{name} created.")
                break
    return


def _execute_test_job(manifest: V1Job) -> None:
    api = _get_batch_api()
    name = manifest.metadata.name
    namespace = settings.namespace()
    api.create_namespaced_job(body=manifest, namespace=namespace)
    w = watch.Watch()

    for event in w.stream(api.list_namespaced_job, namespace=namespace):
        logger.info(
            f"Test Job: {event['object'].metadata.name} "
            f"{event['object'].status.active} running."
        )
        if event["object"].metadata.name == name:
            if event["object"].status.active == 1:
                w.stop()
                logger.info(f"{name} started.")
                break
    return


def run_test(
    project: Project,
    config_content: str,
    test_id: int,
    test_group_id: int,
    app_image_name: str,
) -> None:
    config_file, config_folder = project.config_path.rsplit("/", 1)

    config_map_manifest = templates.config_map(test_id, {config_file: config_content})
    _execute_config_map(config_map_manifest)

    if project.two_container:
        pod_manifest = templates.test_job(
            test_id,
            app_image_name,
            config_folder,
            project.tester_command,
            project.result_path,
            test_group_id,
            project.tester_image,
        )
    else:
        pod_manifest = templates.test_job(
            test_id,
            app_image_name,
            config_folder,
            project.tester_command,
            project.result_path,
            test_group_id,
        )

    _execute_test_job(pod_manifest)
    return
