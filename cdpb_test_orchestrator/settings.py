import configparser
import os


def get_config():
    debug_env = os.environ.get("DEBUG")
    mount_env = os.environ.get("MOUNT")

    if debug_env == "on":
        config = configparser.ConfigParser()
        with open("config/test.ini", "r") as f:
            config.read_file(f)
        config["ENV"] = {"DEBUG": "on"}
    else:
        config = configparser.ConfigParser()
        with open("config/production.ini", "r") as f:
            config.read_file(f)
        config["ENV"] = {"DEBUG": "off"}

    if mount_env:
        config["NFS"]["mount"] = mount_env
    return config
