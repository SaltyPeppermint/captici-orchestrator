from kubernetes import config
from kubernetes.client.api import core_v1_api
from kubernetes.client.configuration import Configuration
from ..settings import *
import time


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
    api_instance = get_kube_api()

    name = manifest["metadata"]["name"]
    resp = None

    print(f"Creating pod {name} ...")

    resp = api_instance.create_namespaced_pod(body=manifest,
                                              namespace=NAMESPACE)
    while True:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=NAMESPACE)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)
    print("Done.")
    return
