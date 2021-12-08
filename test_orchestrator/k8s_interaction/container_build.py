from typing import Dict, List
from settings import config

from k8s_interaction import k8s_api
from k8s_interaction import templates
from storage import projects
from storage import repositories as repos
from storage import reports
from storage import tars


def build_app(project_id: int, commit_hash: str) -> str:
    tar_id = tars.tar_into(project_id, commit_hash)
    project_name = projects.id2name(project_id)
    build_name = f"kaniko-{project_id}-{project_name}-{commit_hash}"

    registry_url = config["Registry"]["url"]
    registry_user = config["Registry"]["user"]
    image_name = f"{registry_url}/{registry_user}/{project_id}-{project_name}:{commit_hash}"

    pod_manifest = templates.build_pod(build_name, image_name, tar_id)
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
        report_id = reports.ReportInfo(
            project_id, commit_hash, test_id).serialize()
        app_config_map_name = f"{identifier}-app-config"

        config_map_manifest = templates.config_map(
            app_config_map_name, app_configs[test_id])

        if(is_two_container):
            pod_manifest = templates.two_pods(
                identifier, app_image_name, tester_image_name, app_config_map_name, app_config_mount, tester_env, report_id)
        else:
            pod_manifest = templates.one_pod(
                identifier, app_image_name, app_config_map_name, app_config_mount, tester_env, report_id)

        k8s_api.execute_manifest(config_map_manifest)
        k8s_api.execute_manifest(pod_manifest)

    return
