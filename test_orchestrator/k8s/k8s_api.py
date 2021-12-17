import time

from kubernetes import config as kubeconfig
from kubernetes.client.api import core_v1_api
from kubernetes.client.configuration import Configuration
from sqlalchemy.orm import Session
from test_orchestrator import storage
from test_orchestrator.settings import config

from . import templates


def get_kube_api() -> core_v1_api.CoreV1Api:
    kubeconfig.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def execute_pod_manifest(manifest) -> None:
    api = get_kube_api()

    name = manifest["metadata"]["name"]
    namespace = config["K8s"]["namespace"]
    resp = None

    resp = api.create_namespaced_pod(body=manifest, namespace=namespace)
    while True:
        resp = api.read_namespaced_pod(name=name, namespace=namespace)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)
    print(f"{name} scheduled.")


def await_pod_manifest(manifest) -> None:
    api = get_kube_api()

    name = manifest["metadata"]["name"]
    namespace = config["K8s"]["namespace"]
    resp = None
    while True:
        resp = api.read_namespaced_pod(name=name, namespace=namespace)
        if resp.status.phase != "Succeeded":
            break
        time.sleep(1)
    print(f"{name} succeeded.")
    return


def execute_config_map_manifest(manifest) -> None:
    api = get_kube_api()

    name = manifest["metadata"]["name"]
    namespace = config["K8s"]["namespace"]
    resp = None

    resp = api.create_namespaced_config_map(body=manifest, namespace=namespace)
    while True:
        resp = api.read_namespaced_config_map(name=name, namespace=namespace)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)
    print(f"{name} scheduled.")


def await_config_map_manifest(manifest) -> None:
    api = get_kube_api()

    name = manifest["metadata"]["name"]
    namespace = config["K8s"]["namespace"]
    resp = None

    while True:
        resp = api.read_namespaced_config_map(name=name, namespace=namespace)
        if resp.status.phase != "Succeeded":
            break
        time.sleep(1)
    print(f"{name} succeeded.")
    return


def build_commit(db: Session, project_id: int, commit_hash: str) -> str:
    tar_path = storage.tars.tar_into(db, project_id, commit_hash)
    reg_url = config["Registry"]["url"]
    reg_user = config["Registry"]["user"]
    image_name = f"{reg_url}/{reg_user}/{project_id}:{commit_hash}"

    pod_manifest = templates.pod_builder_pod(project_id, image_name, tar_path)
    execute_pod_manifest(pod_manifest)
    await_pod_manifest(pod_manifest)
    return image_name


def get_project_meta(db, project_id):
    config_path = storage.projects.id2config_path(db, project_id)
    tester_command = storage.projects.id2tester_command(db, project_id)
    result_path = storage.projects.id2result_path(db, project_id)
    is_two_container = storage.projects.id2is_two_container(db, project_id)
    return config_path, tester_command, result_path, is_two_container


def run_container_test(
    db: Session,
    project_id: int,
    config_id: int,
    test_id: int,
    test_group_id: int,
    app_image_name: str,
) -> None:

    config_path, tester_command, result_path, two_container = get_project_meta(
        db, project_id
    )
    config_file, config_folder = config_path.rsplit("/", 1)

    config_content = storage.configs.id2content(db, config_id)
    config_map_manifest = templates.config_map(test_id, {config_file: config_content})

    if two_container:
        tester_image_name = storage.projects.id2tester_image(db, project_id)
        pod_manifest = templates.pod(
            test_id,
            app_image_name,
            config_folder,
            tester_command,
            result_path,
            test_group_id,
            tester_image_name,
        )
    else:
        pod_manifest = templates.pod(
            test_id,
            app_image_name,
            config_folder,
            tester_command,
            result_path,
            test_group_id,
        )

    execute_config_map_manifest(config_map_manifest)
    await_config_map_manifest(config_map_manifest)

    execute_pod_manifest(pod_manifest)
    return
