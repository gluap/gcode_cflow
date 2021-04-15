gcode-cflow
===========
A rudimentary g-code filter to experimentally make feedrate dependent extrusion adjustments to g-code for 3D printers.

Different sources suggest that at high extrusion speeds, filament deformation in the extruder due to back pressure
leads to a dynamic underextrusion. The higher the extrusion speed, the higher the back pressure and the lower the
amount of filament actually extruded. One good explanation can be found `here <https://youtu.be/0xRtypDjNvI>`_.
this happens way before extruder slipping.

This is a small g-code filter script that does the following:

- Read a given g-code file
- Use the configured known underextrusion values at different volumetric flow rates to compensate for the backpressure
- Output modified g-code

**This will be detrimental to print quality of small details:**
This will only be useful (if at all) for large models with long edges. At high feed rates even with high accelerations
above 4000 mm/s², acceleration from zero to x/y feeds of 100 and above mm/s takes a few mm.
So for models and details below a few mm this compensation will actually be detrimental to print quality by causing
over-extrusion during acceleration and deceleration.

Implemented in firmware this shortcoming could be avoided because during motion planning the exact extruder speed
is always known.

Setup:
------
Installieren (aktueller python interpreter erforderlich) per::

   pip install git+https://github.com/gluap/gcode_cflow.git

Usage:
------
Assuming you have already measured your feedrate dependent extrusion and created your config file, with calibration
data, this filter can be run as follows to apply the correction::

    cflow ./test.gcode --config ./tests/files/testconfig.yml

or if you want some debug output in your g-code output you can add ``--debug``, the resulting g-code will
then contain the original g-code as follows::

    G1 X92.813 Y78.479 E0.05851;was: G1 X92.813 Y78.479 E0.05851 e=7.81005944548757 mm³/s
    G1 X93.546 Y78.030 E0.02907;was: G1 X93.546 Y78.030 E0.02907 e=7.803128087186357 mm³/s
    G1 X94.286 Y77.594 E0.02907;was: G1 X94.286 Y77.594 E0.02907 e=7.809433201922295 mm³/s
    G1 X95.798 Y76.756 E0.05851;was: G1 X95.798 Y76.756 E0.05851 e=7.809528195040778 mm³/s
    G1 X96.557 Y76.361 E0.02898;was: G1 X96.557 Y76.361 E0.02898 e=7.81491476716116 mm³/s
    G1 X98.108 Y75.604 E0.05842;was: G1 X98.108 Y75.604 E0.05842 e=7.810250439017135 mm³/s


Measuring your feedrate dependent extrusion offsets
---------------------------------------------------

To use the script, calibration data needs to be taken for your printer + filament + nozzle temperature.

For calibration you need:
 - A scale with decent precision, 0.01g is preferable to waste less filament. If you have a coarser scale you can
   increase the amount of filament extruded in the g-code or instead measure the length of filament pulled in by the
   extruder (come up with your own measurement scheme).
 - Your 3D-Printer
 - The G-Code to extrude a defined amount of filament `from cnc kitchen <https://www.cnckitchen.com/blog/testing-bimetallic-heat-breaks>`_

To create your calibration file use the following steps:
 - create g-code files using abovementioned template
    - that use your preferred temperature
    - with different volumetric flow rates from the range of flow rates you will want to print with
 - for instance I used: 1, 3, 5, 10 mm³/s, chose your own intervals.
 - run test extrusions at your chosen flow rates

   - start printing with one of your g-codes
   - shortly after starting there should be a two second break (``G4 S2``, replace with ``G4 P2000`` if you do
     not observe extrusion taking a 2 second brake shortly after printing begins). During the break,
     remove the filament pushed out by the pre-extrusion step.
   - wait until extrusion finishes
   - immediately after extrusion finishes take your spaghetti away from the nozzle (to avoid weighing oozed
     filament later)
   - weigh your spaghetti and write down the result

You will end up with a table of flow rates and corresponding filament weights like mine below:

.. list-table:: extrusion rates
   :widths: 20, 20
   :header-rows: 1

   * - volumetric flow speed [mm³/min]
     - extruded filament weigth [g]
   * - 1.0
     - 0.6
   * - 3.0
     - 0.57
   * - 5.0
     - 0.55
   * - 10
     - 0.51

If not contained in the table the code assumes that the desired weight of extruded filament is equal to the one
indicated for to the lowest speed indicatated in the table, but you can also calculate it too to make sure that it
matches. The process is described at the end of the readme file.

Enter the values you determined into a config file like so::

    # the feed rates at which extrusion values have been measured in mm³/s
    values_speeds: [ 1, 3, 5, 10 ]
    # the actual amount of filament extruded for the volumetric speeds above
    values_extruded: [ 0.6, 0.57, 0.55, 0.51 ]

Optional: Calculating the ideal extrusion amount:
'''''''''''''''''''''''''''''''''''''''''''''''''

The speed at 0 can never be measured, but if you want to
calculate it you can simply multiply the amount of filament extruded in the ideal case. For a 200mm length *l*
of 1.75mm diameter *d* filament of density ρ (PLA: *ρ*=1.24g/cm³) expected mass *m* equals to:

.. math::
   m = l\cdot \left(\frac{d}{2}\right)^{2} \pi \cdot \rho

in my case the expected value for *m* would be calculated as:

.. math::
   m = l\cdot \left(\frac{d}{2}\right)^{2} \pi \cdot \rho = 200\mathrm{mm}\cdot\frac{1.75\mathrm{mm}}{2}^2\pi\cdot 1.24 \frac{\mathrm{g}}{\mathrm{cm}³}=0.5965g

*m* = 0.5965 is pretty close to the 0.60 I measured, so it seems that indeed at low speeds the extrusion
is working as it should.

If your even low speed extrusion isn't rather near to the calculated value, you may want to check your e-steps.

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