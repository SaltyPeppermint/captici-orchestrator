import configparser
import os


def get_config():
    debug_env = os.environ.get("DEBUG")
    mount_env = os.environ.get("MOUNT")

    if debug_env == "on":
        config = configparser.ConfigParser()
        config.read_file(open("config/test.ini"))
        config["ENV"] = {"DEBUG": "on"}
    else:
        config = configparser.ConfigParser()
        config.read_file(open("config/production.ini"))
        config["ENV"] = {"DEBUG": "off"}

    if mount_env:
        config["NFS"]["mount"] = mount_env
    return config
