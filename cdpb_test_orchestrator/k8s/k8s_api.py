import time

from cdpb_test_orchestrator.data_objects import Project
from cdpb_test_orchestrator.settings import get_config
from kubernetes import config as kubeconfig
from kubernetes.client.api import core_v1_api
from kubernetes.client.configuration import Configuration
from kubernetes.client.models.v1_config_map import V1ConfigMap
from kubernetes.client.models.v1_pod import V1Pod

from . import templates


def get_kube_api() -> core_v1_api.CoreV1Api:
    config = get_config()
    if config["ENV"]["DEBUG"] == "on":
        kubeconfig.load_kube_config()
        try:
            c = Configuration().get_default_copy()
        except AttributeError:
            c = Configuration()
            c.assert_hostname = False
        Configuration.set_default(c)

    else:
        kubeconfig.load_incluster_config()
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def execute_pod_manifest(manifest: V1Pod) -> None:
    api = get_kube_api()

    name = manifest.metadata
    config = get_config()
    namespace = config["K8s"]["namespace"]
    resp = None

    resp = api.create_namespaced_pod(body=manifest, namespace=namespace)
    while True:
        resp = api.read_namespaced_pod(name=name, namespace=namespace)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)
    print(f"{name} scheduled.")
    return


def execute_build_pod_manifest(manifest: V1Pod) -> None:
    api = get_kube_api()

    name = manifest.metadata
    config = get_config()
    namespace = config["K8s"]["namespace"]
    resp = None

    resp = api.create_namespaced_pod(body=manifest, namespace=namespace)
    while True:
        resp = api.read_namespaced_pod(name=name, namespace=namespace)
        if resp.status.phase != "Succeeded":
            break
        time.sleep(1)
    print(f"{name} scheduled.")
    return


def execute_config_map_manifest(manifest: V1ConfigMap) -> None:
    api = get_kube_api()

    name = manifest.metadata.name
    config = get_config()
    namespace = config["K8s"]["namespace"]
    api.create_namespaced_config_map(body=manifest, namespace=namespace)
    print(f"{name} scheduled.")
    return


def build_commit(
    tar_path: str, project_id: int, commit_hash: str, dockerfile_path: str
) -> str:
    config = get_config()
    reg_url = config["Registry"]["url"]
    reg_user = config["Registry"]["user"]
    image_name = f"{reg_url}/{reg_user}/{project_id}:{commit_hash}"
    build_id = f"{project_id}-{commit_hash}"

    pod_manifest = templates.pod_builder_pod(
        build_id, image_name, tar_path, dockerfile_path
    )
    execute_build_pod_manifest(pod_manifest)
    return image_name


def run_test(
    project: Project,
    config_content: str,
    test_id: int,
    test_group_id: int,
    app_image_name: str,
) -> None:
    config_file, config_folder = project.config_path.rsplit("/", 1)

    config_map_manifest = templates.config_map(test_id, {config_file: config_content})
    execute_config_map_manifest(config_map_manifest)

    if project.two_container:
        pod_manifest = templates.pod(
            test_id,
            app_image_name,
            config_folder,
            project.tester_command,
            project.result_path,
            test_group_id,
            project.tester_image,
        )
    else:
        pod_manifest = templates.pod(
            test_id,
            app_image_name,
            config_folder,
            project.tester_command,
            project.result_path,
            test_group_id,
        )

    execute_pod_manifest(pod_manifest)
    return
