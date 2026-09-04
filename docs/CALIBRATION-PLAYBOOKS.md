# Calibration playbooks

Checklists for the events that invalidate calibration. Hard-won rules from
Aug–Sep 2026 sessions are marked ⚠. Instruments live in two lanes:

- **Macro suite** (printer-side, parametric, no slicer): `TEMPERATURE_TOWER`,
  `PA_PATTERN`, `PRESSURE_ADVANCE_CALIBRATION`, `STRINGING_TEST`
- **OrcaSlicer → Calibration menu** (profile-accurate; use when the result
  feeds a profile field)

⚠ **Z instrument of record**: Orca-sliced single-layer pads, Z-laddered with
`SET_GCODE_OFFSET` between pads. Macro-drawn gapped-line squares under-read
squish (0.340 incident) — never calibrate Z from them.

---

## New nozzle (replacement or size change)

1. Heat to working temp, wipe, cold-pull if switching materials.
2. ⚠ Re-verify `[probe] z_offset` (nozzle length changed): fresh
   `G28` + `QUAD_GANTRY_LEVEL` + `G28 Z` **per round** (a stale Z reference
   drifts 0.03–0.05), then the pad Z-ladder. Update `microprobev2.cfg`.
3. Size change only: new Orca process profile (line widths, layer bounds),
   then flow (EM ladder), then PA (`PA_PATTERN` — PA shifts with nozzle dia).
4. Verification print (benchy-shifted or one small functional part).

## New filament (brand / type / color change within brand)

1. **Dry first** (PolyDryer): PLA level 1, PETG level 2; expect 15–30% RH
   ⚠ indoors with AC — ambient humidity sets the floor. Orange desiccant.
2. Spoolman: create spool entry, set weight; load filament.
3. Temperature: `TEMPERATURE_TOWER HOTEND_TEMPERATURE=<mid> BED_TEMPERATURE=<mat>`
   (offsets sweep downward) — or Orca temp tower. Pick temp.
4. New material family only — flow: EM ladder squares at chosen temp.
5. PA: `PA_PATTERN HOTEND_TEMP=<chosen>` (or Orca PA pattern). Set in
   filament profile (future: Spoolman extra field read by PRINT_START).
6. Retraction: `STRINGING_TEST HOTEND_TEMP=<chosen> BED_TEMP=<mat>`
   (defaults sweep 0.2→1.0mm in 5 bands). Cleanest band → profile.
7. Bed temp / adhesion: material preset (PLA 60–65, PETG 75–80), washed plate.
8. Save Orca filament profile AND export the flattened copy to
   `slicer-profiles/orca/cli-full/` (CLI slicing reads only from there).
9. Verification benchy. ⚠ Feed-path drag check if printing from a drybox.

## New build plate / surface

1. ⚠ Wash with dish soap before first use.
2. Z re-check: pad ladder (sheet thickness differs plate-to-plate; the two
   plates measured 0.13 apart).
3. km bed_surface entry if keeping both plates (offset persists in
   variables.cfg — zero it when re-baking config z_offset).

## After MCU firmware reflash

⚠ The v0.13.0-733 reflash shifted the probe Z reference ~0.13mm. After ANY
MCU firmware change: re-verify Z with the pad ladder before trusting a print.

## After physically moving the printer

1. Check every bay connector (the Aug–Sep saga: motor phase crimps, CAN
   junction, USB) — wiggle-test under the CAN monitor if suspicious.
2. `G28` + `QUAD_GANTRY_LEVEL` + fresh mesh.
3. `SHAPER_CALIBRATE` (input shaper values are position/surface dependent).
4. Belt tension sanity check.

## Reading results back into the system

Calibration results live in three places — keep them agreeing:
- `[probe] z_offset` → `config/microprobev2.cfg` (committed; auto-backup
  pushes hourly — verify push works: `git -C ~/printer_data status`)
- PA / retraction / temps → Orca profiles (+ `slicer-profiles/orca/cli-full/`)
- Per-surface tweaks → km babysteps (auto-persisted to variables.cfg)
