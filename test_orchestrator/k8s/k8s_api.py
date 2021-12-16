import time

from kubernetes import config
from kubernetes.client.api import core_v1_api
from kubernetes.client.configuration import Configuration
from sqlalchemy.orm import Session
from test_orchestrator import storage
from test_orchestrator.settings import config

from . import templates


def get_kube_api() -> core_v1_api.CoreV1Api:
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def execute_manifest(manifest) -> None:
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
    print("Done.")
    return


def build_commit(db: Session, project_id: int, commit_hash: str) -> str:
    tar_path = storage.tars.tar_into(project_id, commit_hash)
    project_name = storage.projects.id2name(db, project_id)
    build_name = f"kaniko-{project_id}-{project_name}-{commit_hash}"

    registry_url = config["Registry"]["url"]
    registry_user = config["Registry"]["user"]
    image_name = f"{registry_url}/{registry_user}/{project_id}-{project_name}:{commit_hash}"

    pod_manifest = templates.build_pod(build_name, image_name, tar_path)
    execute_manifest(pod_manifest)
    return image_name


def run_container_test(
        db: Session,
        project_id: int,
        test_id: int,
        app_image_name: str) -> None:

    identifier = f"test-{test_id}"
    config_id = storage.tests.id2config_id(db, test_id)
    config_mount = storage.projects.id2config_path(db, project_id)

    config_map_name = f"config-{identifier}"
    config_content = storage.configs.id2content(db, config_id)
    config_map_manifest = templates.config_map(
        config_map_name, config_content)

    tester_command = storage.projects.id2tester_command(db, project_id)
    is_two_container = storage.projects.id2is_two_container(db, project_id)
    if(is_two_container):
        tester_image_name = storage.projects.id2tester_image(
            db, project_id)
        pod_manifest = templates.two_pod(
            identifier, app_image_name, tester_image_name, config_map_name, config_mount, tester_command, test_id)
    else:
        pod_manifest = templates.one_pod(
            identifier, app_image_name, config_map_name, config_mount, tester_command, test_id)

    execute_manifest(config_map_manifest)
    execute_manifest(pod_manifest)
    return
