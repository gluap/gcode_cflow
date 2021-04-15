from gcode_cflow.gcodefilter import GcodeFilter


def main():
    in_gcode = open("../test.gcode", "r").readlines()
    gw = GcodeFilter(in_gcode)
    out_gcode = open("../test_out.gcode", "w")
    while gw.lines_left:
        line = gw.read_line()
        out_gcode.write(line)
        print(line)

if __name__ == "__main__":
    main()
