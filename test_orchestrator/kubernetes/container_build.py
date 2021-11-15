from typing import Dict, List
from ..settings import *

from ..kubernetes import k8s_api
from ..kubernetes import templates
from ..storage import projects
from ..storage import repositories as repos


def build_app(project_id: int, commit_hash: str) -> str:
    repos.tar_into(project_id, commit_hash)
    project_name = projects.id2name(project_id)
    tar_path = f"/tars/{project_id}-{project_name}/{commit_hash}.tar.gz"
    build_name = f"kaniko-{project_id}-{project_name}-{commit_hash}"
    image_name = f"{CONTAINER_REGISTRY_URL}/{CONTAINER_REGISTRY_USER}/{project_id}-{project_name}:{commit_hash}"

    pod_manifest = templates.build_pod(build_name, image_name, tar_path)
    k8s_api.execute_manifest(pod_manifest)
    return image_name


def run_tests(project_id: int, commit_hash: str, tester_env: str, app_configs: List[Dict[str, str]]):
    is_two_container = projects.is_two_container(project_id)
    app_config_mount = projects.id2app_config_mount(project_id)
    project_name = projects.id2name(project_id)
    app_image_name = build_app(project_id, commit_hash)
    if(is_two_container):
        tester_image_name = projects.id2tester_image_name(project_id)

    for test_id in range(len(app_configs)):
        identifier = f"test-{test_id}-{project_id}-{project_name}-{commit_hash}"
        app_config_map_name = f"{identifier}-app-config"

        config_map_manifest = templates.config_map(
            app_config_map_name, app_configs[test_id])

        if(is_two_container):
            pod_manifest = templates.two_pods(
                identifier, app_image_name, tester_image_name, app_config_map_name, app_config_mount, tester_env)
        else:
            pod_manifest = templates.one_pod(
                identifier, app_image_name, app_config_map_name, app_config_mount, tester_env)

        k8s_api.execute_manifest(config_map_manifest)
        k8s_api.execute_manifest(pod_manifest)

    return
