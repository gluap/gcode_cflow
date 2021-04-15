Flow compensator
================
A rudimentary g-code filter to make extruder-speed dependent adjustments to g-code

Different sources suggest that at high extrusion speeds, filament deformation in the extruder due to back pressure
leads to a dynamic underextrusion. The higher the extrusion speed, the higher the back pressure and the lower the
amount of filament actually extruded. One good explanation can be found `here <https://youtu.be/0xRtypDjNvI>`_

This is a small g-code filter script that does the following:

- Read a given g-code file
- Use the configured known underextrusion values at different volumetric flow rates to compensate for the backpressure
- Output modified g-code

Known shortcomings
------------------
At the time of g-code writing the real extruder speed for a given move is unknown. It is only computed by the
printer firmware during motion planning, the F-value set during g-code generation is only the maximum allowed speed
and the actual speed of the nozzle will be lower due to limits to feed rates and accelerations in printer firmware.
For this reason the optimal location to implement this kind of flow compensation would be in printer firmware.

**Missing Features:**
- Only g-code using relative extrusions can be processed (I use Prusa Slicer)
- Arc moves are not supported (but the output can be arcified by ArcWelder if desired

Keep in mind that this is meant to be a demonstrator to evaluate whether the feature would be helpful

Usage
-----

First calibration data needs to be taken for your printer + filament + nozzle temperature.
To do so I created a table of extrusion speeds