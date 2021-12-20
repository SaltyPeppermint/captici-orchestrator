import os


def is_debug() -> bool:
    debug_env = os.environ.get("DEBUG")
    if debug_env == "on":
        return True
    else:
        return False


def repos_dir() -> str:
    mount_env = os.environ.get("MOUNT")
    if mount_env is None:
        mount_env = "/var/nfs"

    return mount_env + "/repos"


def tars_dir() -> str:
    mount_env = os.environ.get("MOUNT")
    if mount_env is None:
        mount_env = "/var/nfs"

    return mount_env + "/tars"


def namespace() -> str:
    namespace = os.environ.get("NAMESPACE")
    if namespace is None:
        namespace = "cdpb-tester"
    return namespace


def reg_url() -> str:
    reg_url = os.environ.get("REG_URL")
    if reg_url is None:
        reg_url = "registry.kube.informatik.uni-leipzig.de"
    return reg_url


def reg_user() -> str:
    reg_user = os.environ.get("REG_USER")
    if reg_user is None:
        reg_user = "cdpb-test-orchestrator"
    return reg_user


def db_type() -> str:
    db_type = os.environ.get("db_type")
    if db_type is None:
        db_type = "sqlite"
    return db_type


def db_location() -> str:
    db_location = os.environ.get("DB_LOCATION")
    if db_location is None:
        db_location = "/var/nfs"
    return db_location
