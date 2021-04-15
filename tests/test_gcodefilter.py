import os

from pathlib import Path

from gcode_cflow.gcodefilter import GcodeFilter



def test_gcode():
    gcode = "G1 F125\nG1 E200".split("\n")
    gc = GcodeFilter(gcode, config=Path(os.path.join(os.path.dirname(__file__), "files/testconfig.yml")))
    assert gc.read_line() == "G1 F125\n"
    assert gc.read_line() == "G1 E218.21948\n"
