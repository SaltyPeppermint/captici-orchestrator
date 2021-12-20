import logging

from cdpb_test_orchestrator import settings
from cdpb_test_orchestrator.data_objects import Project
from kubernetes import config, watch
from kubernetes.client.api.batch_v1_api import BatchV1Api
from kubernetes.client.api.core_v1_api import CoreV1Api
from kubernetes.client.configuration import Configuration
from kubernetes.client.models.v1_config_map import V1ConfigMap
from kubernetes.client.models.v1_job import V1Job

from . import templates


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


def execute_build_job(manifest: V1Job) -> None:
    api = _get_batch_api()
    name = manifest.metadata
    namespace = settings.namespace()
    api.create_namespaced_job(body=manifest, namespace=namespace)

    w = watch.Watch()
    for event in w.stream(api.list_namespaced_job, namespace=namespace):
        logging.info(
            f"Build Job: {event['object'].metadata.name} "
            f"{event['object'].status.succeeded} succeeded."
        )
        if event["object"].metadata.name == name:
            if event["object"].status.succeeded == 1:
                w.stop()
                logging.info(f"{name} finished.")
                return


def build_commit(
    tar_path: str, project_id: int, commit_hash: str, dockerfile_path: str
) -> str:
    reg_url = settings.reg_url()
    reg_user = settings.reg_user()
    image_name = f"{reg_url}/{reg_user}/{project_id}:{commit_hash}"
    build_id = f"{project_id}-{commit_hash}"

    pod_manifest = templates.build_job(build_id, image_name, tar_path, dockerfile_path)
    execute_build_job(pod_manifest)
    return image_name


def _execute_config_map(manifest: V1ConfigMap) -> None:
    api = _get_core_api()
    name = manifest.metadata.name
    namespace = settings.namespace()
    api.create_namespaced_config_map(body=manifest, namespace=namespace)

    w = watch.Watch()
    for event in w.stream(api.list_namespaced_config_map, namespace=namespace):
        logging.info(f"ConfigMap: {event['object'].metadata.name} {event['type']}")
        if event["object"].metadata.name == name:
            if event["type"] == "ADDED":
                w.stop()
                logging.info(f"{name} created.")
                return


def _execute_test_job(manifest: V1Job) -> None:
    api = _get_batch_api()
    name = manifest.metadata
    namespace = settings.namespace()
    api.create_namespaced_job(body=manifest, namespace=namespace)
    w = watch.Watch()

    for event in w.stream(api.list_namespaced_job, namespace=namespace):
        logging.info(
            f"Test Job: {event['object'].metadata.name} "
            f"{event['object'].status.active} running."
        )
        if event["object"].metadata.name == name:
            if event["object"].status.active == 1:
                w.stop()
                logging.info(f"{name} started.")
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
