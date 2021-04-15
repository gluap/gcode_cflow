# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import logging
import math
import re
from collections import deque
from pathlib import Path

from scipy.interpolate import interp1d

from .config import load_config

logger = logging.getLogger(__name__)

M83 = re.compile("[^;]*M83", flags=re.IGNORECASE)
M82 = re.compile("[^;]*M82", flags=re.IGNORECASE)
G1 = re.compile("G[0]?1")
GARC = re.compile("G[0]?[23]\s+")

X = re.compile("X(?P<x>[0-9.]+)")
Y = re.compile("Y(?P<y>[0-9.]+)")
Z = re.compile("Z(?P<z>[0-9.]+)")
E = re.compile("E(?P<e>[0-9.]+)")

F = re.compile("F(?P<feed>\d+)")


class GcodeFilter:
    def __init__(self, gcode, debug=False, config=Path.home() / "gcode_cflow.cfg"):
        self.interpolation = lambda x: 1.0
        self.configfile = config
        self.gcode_queue = deque(gcode)
        self.output = []
        self.absolute = True
        self.f = 150
        self.x = 0
        self.y = 0
        self.z = 0
        self.e = 0
        self.xstep = 0
        self.ystep = 0
        self.zstep = 0
        self.estep = 0
        self.debug = debug
        self.init_interpolation()

    def init_interpolation(self):
        config = load_config(self.configfile)
        self.interpolation = interp1d(config.values_speeds, [config.reference/e for e in config.values_extruded])

    @property
    def lines_left(self):
        return len(self.gcode_queue) > 0

    def read_line(self):
        line = self.gcode_queue.popleft().strip()
        if M83.match(line):
            self.absolute = False
            return line + "\n"
        if M82.match(line):
            self.absolute = True
            return line + "\n"
        if G1.match(line):
            line = self.process_move(line)
            return line + "\n"
        if GARC.match(line):
            raise Exception("arc moves not supported")
        return line + "\n"

    def process_move(self, line):
        self.check_for_feed_change(line)
        return self.adapt_extrusion_if_present(line)

    def check_for_feed_change(self, line):
        f_in_line = F.search(line)
        if f_in_line:
            self.f = float(f_in_line.groupdict()["feed"])

    @property
    def speed_in_qmms(self):
        time = (self.xstep ** 2 + self.ystep ** 2 + self.estep ** 2) ** 0.5 / self.f * 60.
        return self.estep * (1.75 ** 2 / 4) * math.pi / time if time > 0 else 0

    @property
    def adapted_feed(self):
        feed_factor = self.interpolation(self.speed_in_qmms)
        return self.estep * feed_factor

    @property
    def adapted_evalue(self):
        if not self.absolute:
            return self.adapted_feed
        if self.absolute:
            raise Exception("absolute extrusion not implemented, please use relative extrusion in your g-code.")

    def adapt_extrusion_if_present(self, line):
        self.update_coords_and_compute_distance(line)
        new_line = re.sub(E, f"E{self.adapted_feed:.5f}", line)

        line = f"{new_line}"
        if self.debug:
            line += ";was: {line} e={self.speed_in_qmms} mm³/s"
        return line

    def update_coords_and_compute_distance(self, line):
        new_x, new_y, new_z = self.x, self.y, self.z
        x_in_line = X.search(line)
        y_in_line = Y.search(line)
        z_in_line = Z.search(line)
        e_in_line = E.search(line)
        if x_in_line:
            new_x = float(x_in_line.groupdict()["x"])
            self.xstep = new_x - self.x
            self.x = new_x
        else:
            self.xstep = 0
        if y_in_line:
            new_y = float(y_in_line.groupdict()["y"])
            self.ystep = new_y - self.y
            self.y = new_y
        else:
            self.ystep = 0
        if z_in_line:
            new_z = float(z_in_line.groupdict()["z"])
            self.zstep = new_z - self.z
            self.z = new_z
        else:
            self.zstep = 0
        if e_in_line:
            new_e = float(e_in_line.groupdict()["e"])
            if self.absolute:
                self.estep = new_e - self.e
            else:
                self.estep = new_e
            self.e = new_e
        else:
            self.estep = 0
