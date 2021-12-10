import time

from typing import Dict, List
from kubernetes import config
from kubernetes.client.api import core_v1_api
from kubernetes.client.configuration import Configuration

from test_orchestrator.settings import config
from test_orchestrator import storage
from . import templates


def get_kube_api():
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def execute_manifest(manifest):
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


def build_commit(project_id: int, commit: str) -> str:
    tar_id = storage.tars.tar_into(project_id, commit)
    project_name = storage.projects.id2name(project_id)
    build_name = f"kaniko-{project_id}-{project_name}-{commit}"

    registry_url = config["Registry"]["url"]
    registry_user = config["Registry"]["user"]
    image_name = f"{registry_url}/{registry_user}/{project_id}-{project_name}:{commit}"

    pod_manifest = templates.build_pod(build_name, image_name, tar_id)
    execute_manifest(pod_manifest)
    return image_name


def run_tests(project_id: int, commit: str, tester_env: str, app_configs: List[Dict[str, str]]):
    is_two_container = storage.projects.is_two_container(project_id)
    app_config_mount = storage.projects.id2app_config_mount(project_id)
    project_name = storage.projects.id2name(project_id)
    app_image_name = build_commit(project_id, commit)
    if(is_two_container):
        tester_image_name = storage.projects.id2tester_image_name(project_id)

    for test_id in range(len(app_configs)):
        identifier = f"test-{test_id}-{project_id}-{project_name}-{commit}"
        report_id = storage.reports.ReportMeta(
            project_id, commit, test_id).serialize()
        app_config_map_name = f"{identifier}-app-config"

        config_map_manifest = templates.config_map(
            app_config_map_name, app_configs[test_id])

        if(is_two_container):
            pod_manifest = templates.two_pods(
                identifier, app_image_name, tester_image_name, app_config_map_name, app_config_mount, tester_env, report_id)
        else:
            pod_manifest = templates.one_pod(
                identifier, app_image_name, app_config_map_name, app_config_mount, tester_env, report_id)

        execute_manifest(config_map_manifest)
        execute_manifest(pod_manifest)

    return
