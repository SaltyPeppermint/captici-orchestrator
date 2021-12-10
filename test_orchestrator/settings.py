import configparser
import os

env = os.environ.get("DEBUG")
if env == "on":
    config = configparser.ConfigParser()
    config.read_file(open("config/test.ini"))
else:
    config = configparser.ConfigParser()
    config.read_file(open("config/production.ini"))
