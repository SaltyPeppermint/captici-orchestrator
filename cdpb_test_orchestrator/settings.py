import configparser
import os

debug_env = os.environ.get("DEBUG")
mount_env = os.environ.get("MOUNT")

if debug_env == "on":
    config = configparser.ConfigParser()
    config.read_file(open("config/test.ini"))
else:
    config = configparser.ConfigParser()
    config.read_file(open("config/production.ini"))

if mount_env:
    config.set("NFS", "mount", mount_env)
