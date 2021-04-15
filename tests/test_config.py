import os
from pathlib import Path

from gcode_cflow.config import load_config


def test_load_config():
    cfg = load_config(Path(os.path.join(os.path.dirname(__file__), "files/testconfig.yml")))
