# Power & Shutdown Runbook

How to turn this printer off without eating the SD card, and the upgrade path
that removes the human from the loop. Written 2026-09-08.

## Shutting down TODAY (no new hardware)

**Never flip the switch on a running Pi.** The sequence:

1. Soft-shutdown the host — any of:
   - Mainsail (printer.home.arpa) → power icon → **Host → Shutdown**
   - mini12864 → **Setup → Shutdown** (calls Moonraker `shutdown_machine`)
   - `ssh 192.168.1.154 sudo shutdown now`
2. **Wait until the green ACT LED stops flickering** (~20-30s; red PWR stays lit — that's fine, it just means 5V is present).
3. Flip the physical power switch.

Power ON is just the switch: the stack boots to klippy-ready unattended (<1 min, proven repeatedly 2026-09-07).

## The real upgrade: smart plug + Moonraker [power]

A metering smart plug (Shelly Plus Plug US, or anything Tasmota/HA-compatible)
feeding the printer's AC, wired into Moonraker:

```ini
# moonraker.conf addition (Shelly example — set the address after install)
[power printer]
type: shelly
address: <plug-ip>
locked_while_printing: True
restart_klipper_when_powered: True
bound_services: klipper
```

What it buys:
- Mainsail power menu gets a real **Printer On/Off** — the off path can soft-stop
  services first; no more raw switch pulls.
- Auto-on for queued prints, auto-off after print + cooldown (via macro/HA).
- **Power metering** = a log of mains-side voltage/power blips — free evidence
  for the "intermittent upstream 24V event" mystery (2026-09-05).
- Homelab/HA integration (plug speaks local API — no cloud).

Sequencing note: `shutdown_machine` the host first, delay ~30s, then plug off —
HA automation or Moonraker's own delayed off both work. Config to be finalized
when the plug exists.

## PowerPi R3.1 UPS (Joe's drawer stock — bench-test then install)

Single-18650 UPS board: **INPUT 3.9-14V** (screw terminal), **OUTPUT 5V 3A**
(screw terminal + header), seamless battery holdover, ON/OFF switch,
IN/STAT/OUT LEDs. **Pass-through 40-pin header** (female below, male pins
above) — it stacks.

Why: erases the hard-cut failure class entirely — planned cuts, wall-switch
surprises, AND the mystery upstream blips (e.g. the silent Pi reboot
2026-09-07 19:41 would have been a nonevent).

### Stack order (decided 2026-09-08): Pi → CAN HAT → PowerPi ON TOP

- 18650+holder is ~21mm tall — fouls a board above it, so PowerPi rides top.
- Fan on the `5V FAN` pads blows down through the cutout, cooling HAT+Pi.
- Needs the CAN HAT to expose male pins above; if not, one 40-pin stacking
  header (tall female / GPIO riser) between CAN HAT and PowerPi.
- Unknown: which GPIOs (if any) PowerPi touches — bench boot must verify CAN
  chip probes (dmesg mcp251xfd), UART talks, throttled=0x0 with all 3 stacked.

### Wiring (at install — stacked, simpler)

```
24V→5V converter OUT ──► PowerPi INPUT (+/-)     (5V is in the 3.9-14V window)
PowerPi ──► Pi 5V via the stacked header          (remove the direct GPIO-pin feed)
converter OUT (+) ──10kΩ──┬──► GPIO17 (pin 11)  "input present" sense
                          └──20kΩ──► GND         (5V → ~3.3V divider)
```
Fresh 18650 from stock (plenty on hand) — skip old-cell recovery.

GPIO17 is free (CAN HAT uses SPI0 + GPIO25/24; UART uses 14/15). Sense reads
HIGH = mains present, LOW = running on battery.

Bonus: the board has `5V FAN` solder pads beside a 30mm fan cutout — solder a
small 5V fan there for bay airflow (~0.1A, negligible; note it keeps spinning
on battery since the pads are unswitched).

### Shutdown watcher (at install)

systemd service polling GPIO17 (1s): LOW continuously for **60s** (grace for
blips — battery covers them) → `wall` notice → clean `shutdown now`. A single
18650 carries the Pi for ~2h, so 60s grace + orderly halt leaves huge margin.

### Bench test FIRST (board sat unused for years)

1. Measure the 18650: >2.5V = let the board recover/charge it; lower = replace
   the cell (~$6 quality Sanyo/Samsung) — don't gamble on a deeply-drained Li-ion.
2. Input from any USB charger → output must read 5.0-5.25V.
3. Power the Pi from it (printer off): `vcgencmd get_throttled` must stay
   **0x0** under load. Any undervolt bit = board can't carry the Pi = don't install.
4. Pull input mid-run: no reboot, no throttle bits, 2 min on battery, restore.
Pass all four → install during board-swap surgery.

## UPS: deliberately skipped

A signaling UPS protects against *unplanned* outages, but a printer loses the
print anyway unless the UPS carries heaters+motion (huge/expensive). The damage
this machine actually suffered came from *planned* power-offs done uncleanly —
solved above for free. Revisit only if grid blips start corrupting things again
(persistent journald, enabled 2026-09-08, will show them: `journalctl -b -1 -e`).

## SD card strategy

Decision 2026-09-08: replace via **clone**, not fresh install.

1. Soft-shutdown (above), pull the card.
2. On the Mac: clone card → image (`dd` or Raspberry Pi Imager), write image to a
   fresh **SanDisk High/Max Endurance 32-64GB**.
3. New card in printer; old card into a drawer labeled with today's date =
   known-good full system backup.

Write-load reductions already applied (2026-09-08): swap disabled entirely
(8GB RAM, swap measured 0% used), journald persistent but capped 200M.

## Boot LEDs cheat sheet (Pi 4)

| Red PWR | Green ACT | Meaning |
|---|---|---|
| solid | flickering | booting / running normally |
| solid | dead still | not reading SD (bad card/image) — or already halted |
| off/blink | — | 5V power problem (converter, wiring) |
| — | — | wife turned it off |
