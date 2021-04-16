# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import logging
import math
import re
from collections import deque
from enum import Enum
from pathlib import Path

from scipy.interpolate import interp1d

from .config import load_config

logger = logging.getLogger(__name__)

M83 = re.compile("[^;]*M83", flags=re.IGNORECASE)
M82 = re.compile("[^;]*M82", flags=re.IGNORECASE)
G1 = re.compile("G[0]?1")
GARC = re.compile(r"G[0]?[23]\s+")

X = re.compile("X(?P<x>[-0-9.]+)")
Y = re.compile("Y(?P<y>[-0-9.]+)")
Z = re.compile("Z(?P<z>[-0-9.]+)")
E = re.compile("E(?P<e>[-0-9.]+)")

F = re.compile(r"F(?P<feed>[-0-9.]+)")


class LastRetract(Enum):
    CURRENT_LINE = 1
    LAST_LINE = 2
    LONG_AGO = 3


class GcodeFilter:
    def __init__(self, gcode, debug=False, config=Path.home() / "gcode_cflow.cfg"):
        self.interpolation = lambda x: 1.0
        self.configfile = config
        self.gcode_queue = deque(gcode)
        self.output = []
        self.absolute = True
        self.f = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.e = 0
        self.xstep = 0
        self.ystep = 0
        self.zstep = 0
        self.estep = 0
        self.debug = debug
        self.last_extrude = LastRetract.LONG_AGO
        self.init_interpolation()

    def init_interpolation(self):
        config = load_config(self.configfile)
        if not min(config.values_speeds) == 0:
            reference = sorted(zip(config.values_speeds, config.values_extruded))
            c = [(0, reference[0][1]), *reference]
            speeds, weights = list(zip(*c))
        else:
            speeds, weights = [config.values_speeds, config.values_extruded]

        target_value = config.values_extruded[0]
        self.interpolation = interp1d(speeds, [target_value / e for e in weights])

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
        self.update_coords(line)
        return self.adapt_extrusion_if_present(line)

    @property
    def speed_in_qmms(self):
        time = (self.xstep ** 2 + self.ystep ** 2 + self.estep ** 2) ** 0.5 / abs(self.f) * 60.
        return self.estep * (1.75 ** 2 / 4) * math.pi / time if time > 0 else 0

    @property
    def adapted_estep(self):
        if self.last_extrude != LastRetract.LONG_AGO:
            # Last move was a retraction, so we don't modify esteps - retracts are very fast
            # so we likely have no interpolation data for them but they
            # don't create high pressure
            return self.estep
        feed_factor = self.interpolation(abs(self.speed_in_qmms))
        return self.estep * feed_factor

    def adapt_extrusion_if_present(self, line):
        try:
            new_line = re.sub(E, f"E{self.adapted_estep:.5f}", line)
        except:
            print(f"speed: {self.speed_in_qmms}, line: {line}")
            new_line = line

        line = f"{new_line}"
        if self.debug:
            line += f" ; e={self.speed_in_qmms} mm³/s - Original line: {line}"
        return line

    def update_coords(self, line):
        new_x, new_y, new_z = self.x, self.y, self.z
        f_in_line = F.search(line)
        x_in_line = X.search(line)
        y_in_line = Y.search(line)
        z_in_line = Z.search(line)
        e_in_line = E.search(line)
        if f_in_line:
            self.f = float(f_in_line.groupdict()["feed"])
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
            if new_e < 0:
                self.last_extrude = LastRetract.CURRENT_LINE
            elif self.last_extrude == LastRetract.LAST_LINE:
                self.last_extrude = LastRetract.LONG_AGO
        else:
            self.estep = 0
