from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    values_speeds: List[float]
    values_extruded: List[float]


def load_config(path: Path):
    config = None
    with path.open("r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Exception reading yaml file, is it malformed?")
    return Config(**config)
