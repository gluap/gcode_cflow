Results
-------
I have measured the extruded weight of 200mm of filament for my Ender3 and arrived at the following results trying
to compensate feed rate dependent underextrusion

I ran a test print of a g-code file printing a three-perimeter cylinder of about 10cm diameter with three
settings:
- **file 1**: sliced with slow settings with a volumetric flow of about 3mm²/s
- **file 2**: fast at a volumetric flow of 8.2mm³/s (with 100mm/s x/y feed at .2mm layers). I re-ran the same file
- **file 3**: same as file 2 but processed with cflow to compensate for the expected underextrusion.

The expected print weight calculated from the g-code extrusions is 4.825g

The resulting prints were as follows:

- **file 1**: print result was stable even when bending it by hand, weight about 4.78g
- **file 2**: strong vertical wall delamination when bending by hand likely due to underextrusion. weight 4.28g (about 11% underextrusion)
- **file 3**: print result stable even when bending it by hand, weight 4.74g

From this I conclude that the technique works in principle, at least for the simple example of a three-perimeter
cylinder printed at constant speed.

Images:
~~~~~~~
**file 2** Fast print without corrections applied showing delamination:

.. image:: images/delamination.jpg
  :width: 200
  :alt: file 2 delamination

.. image:: images/delamination_2.jpg
  :width: 200
  :alt: file 2 delamination 2

**file 3** Fast print **with** corrections applied showing delamination:

.. image:: images/no_delamination.jpg
  :width: 200
  :alt: file 2 delamination

.. image:: images/no_delamination_2.jpg
  :width: 200
  :alt: file 2 delamination 2

