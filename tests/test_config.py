import os
from gcode_cflow.config import load_config
from pathlib import Path

def test_load_config():
    cfg=load_config(Path(os.path.join(os.path.dirname(__file__), "files/testconfig.yml")))