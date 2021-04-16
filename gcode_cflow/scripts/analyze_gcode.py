from pathlib import Path
import math

from gcode_cflow.gcodefilter import E

import typer


def analyze(input_file: Path = typer.Argument(None, exists=True)):
    if input_file is None:
        typer.echo("need input file as argument, use --help for help")
        return

    in_gcode = open(input_file, "r").readlines()
    e = 0
    for line in in_gcode:
        e_in_line = E.search(line)
        if e_in_line:
            e += float(e_in_line.groupdict()["e"])
    expected_weight = e * 1.24 * (1.75**2/4)*math.pi
    typer.echo(f"expected print total weight (including priming line and everything): {expected_weight}g")



def main():
    typer.run(analyze)


if __name__ == "__main__":
    main()
