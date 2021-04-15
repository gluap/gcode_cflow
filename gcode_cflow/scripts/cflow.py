from pathlib import Path

import typer

from gcode_cflow.gcodefilter import GcodeFilter


def convert(
        input_file: Path = typer.Argument(None, exists=True),
        config: Path = typer.Option(Path.home() / "gcode_cflow.cfg", help="defaults to <USER_HOME>/gcode_cflow.cfg"),
        debug: bool = typer.Option(False)):
    in_gcode = open(input_file, "r").readlines()
    gw = GcodeFilter(in_gcode, config=config, debug=debug)
    out_gcode = open(input_file.parent / (input_file.name + ".converted.gcode"), "w")
    while gw.lines_left:
        line = gw.read_line()
        out_gcode.write(line)


def main():
    typer.run(convert)

if __name__=="__main__":
    main()