import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def set_debug_env():
    # prepare something ahead of all tests
    os.environ["DEBUG"] = "on"
    return
