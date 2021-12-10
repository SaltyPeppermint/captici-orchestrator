import logging
import os
import sys


def testsetup():
    base_path = os.path.realpath(os.path.dirname(__file__))
    root = os.path.join(base_path, "..")
    sys.path.append(root)

    logging.getLogger().addHandler(logging.NullHandler())


testsetup()
