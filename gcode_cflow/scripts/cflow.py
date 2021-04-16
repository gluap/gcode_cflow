from pathlib import Path

import typer

from gcode_cflow.gcodefilter import GcodeFilter


def convert(
        input_file: Path = typer.Argument(None, exists=True),
        config: Path = typer.Option(Path.home() / "gcode_cflow.cfg", help="defaults to <USER_HOME>/gcode_cflow.cfg"),
        debug: bool = typer.Option(False)):
    if input_file is None:
        typer.echo("need input file as argument, use --help for help")
        return

    in_gcode = open(input_file, "r").readlines()
    gw = GcodeFilter(in_gcode, config=config, debug=debug)
    output_filename=input_file.name.replace(".gcode","") + ".converted.gcode"
    out_gcode = open(input_file.parent / output_filename, "w")
    while gw.lines_left:
        line = gw.read_line()
        out_gcode.write(line)
    typer.echo(f"File conversion finished, converted file in {output_filename}")


def main():
    typer.run(convert)

if __name__=="__main__":
    main()