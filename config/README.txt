G-code Banding Test Bundle
==========================

What this is:
- Six tiny test tiles (32x32x6 mm, 0.2 mm layers) that all include a "roof patch" at Z=3.0–3.4 mm.
- The patch is where shiny/smooshed bands typically show up when top solid intersects perimeters.
- Each file changes only one variable so you can see the effect clearly.

IMPORTANT: Preheat your printer to your normal temps. These files do not set temperatures.

Files:
- baseline.gcode : perimeters first; top patch is slow (25 mm/s) and wide (~140%) with full overlap.
- order.gcode    : infill first, then perimeters; top patch prints before rim to keep the rim round.
- overlap.gcode  : patch stays inside by ~0.6 mm (reduced effective overlap), reducing shove into walls.
- speed.gcode    : top patch at 60 mm/s to reduce linger/heat (less "ironed" look).
- flow.gcode     : top patch flow at ~95% (less squish without changing perimeter flow).
- gapfill.gcode  : patch uses narrow lines (like perimeters) to emulate "gap fill off".

How to compare:
1) Print baseline.gcode first and note the band around Z ~3 mm.
2) Print the other variants; look specifically at the band zone:
   - Does the surface look less glossy/smooshed?
   - Are edges less bulged?
   - Does the band "disappear"?

Mapping to slicer settings:
- order.gcode    ->  infill_first = 1  (Print Settings → Advanced → Infill before perimeters)
- overlap.gcode  ->  infill_overlap = 10–12% (keeps infill/patch off the rim)
- speed.gcode    ->  top_solid_infill_speed = 55–60
- flow.gcode     ->  top_infill_extrusion_multiplier ≈ 0.95  (or reduce solid/top extru. width)
- gapfill.gcode  ->  gap_fill = 0  (Infill → Advanced)

Tip:
- If "order" or "overlap" alone clears the band, you can adopt just that change in your real profile.
