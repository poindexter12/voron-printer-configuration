# SB2209 Toolhead Swap: RP2040 → STM32G0B1

**Current safety state, 2026-09-13 ~18:35 PDT:** user disconnected only the
white MicroProbe trigger/sense lead (PB8) with toolhead power off, leaving the
other four leads connected, then restored power. Normal config is loaded for
an isolated electrical test. **Do not home, probe, QGL or print: the physical
trigger signal is disconnected.** Homing is cleared; heaters and motors off.
User confirmed the old external resistor was NOT carried over: the new board
uses its single five-pin BLTouch connector.

Replacing the SB2209 CAN **RP2040** board (convicted 2026-09-07: its can2040
software CAN bus-offs under ANY motion — see project memory) with the SB2209
CAN V1.0 **STM32G0B1** board (hardware FDCAN). Same form factor, same
Stealthburner wiring harness — the toolhead-side connectors move over 1:1.

G0B1 configs activated on 2026-09-13:
- `config/sb2209-g0b1-canbus.cfg` (toolhead hardware, G0B1 pins)
- `config/microprobev2-g0b1.cfg` (probe, G0B1 pins — VERIFY before homing)

## 2026-09-13 bring-up: full config restored after diagnostics

The STM32G0B1 board is installed and flashed. **Printer is on its side; no
motion or heating until reassembled and explicitly cleared.**

- Klipper `v0.13.0-745-gf0892d82`, G0B1 / 8MHz / 8KiB / CAN PB0/PB1 at 1M.
- Katapult `v0.0.1-106-g399e50e`, USB PA11/PA12, application offset 8KiB,
  double-reset entry enabled. Future firmware uploads require temporary USB;
  this is not a CAN Katapult build.
- New CAN UUID: `bbe5305878fd`. Pi `25-can.network` changed to `BitRate=1M`.
- Original 128KiB flash backed up; Katapult readback compared byte-for-byte;
  Klipper upload verified by Katapult.
- Firmware, build configs, backups and diagnostic results on the Pi:
  `~/firmware/sb2209-g0b1-20260913-145955/`.
- Sensor-only diagnostics temporarily used `kinematics: none`, no steppers,
  heaters, probe outputs, includes or startup macros. The old normal config is
  preserved as `printer.cfg.before-comms` in that firmware directory;
  `comms-only.cfg` is the diagnostic copy.
- **Full configuration restored and live-verified at ~15:22 PDT**, on the Pi
  and in the Mac repo, with both G0B1 includes. Deployment snapshot is in
  `full-setup/` in the firmware directory. Klipper ready, every motor disabled,
  both heaters target/power zero, fans off, toolhead CAN errors/retries zero.
  No motion, probe deployment or heating was commanded.
- Corrected reversed staged fan pins to the installed BTT sample:
  part cooling `PA0`, hotend cooling `PA1`. Confirm fan identity before heating.
- Initial readings: hotend ~26°C, board/MCU ~32°C; both MCUs connected.
- Diagnostic script `comms-test.py` streams ADXL345 via the Klipper API at
  3200 samples/sec for five minutes, without issuing G-code. Hardware SPI
  `spi2_PB2_PB11_PB10` is supported by the installed Klipper build.
- **Stationary test passed, 15:09–15:14 PDT:** 300 seconds, 946150 ADXL samples
  (~3153 samples/sec measured at the configured 3200 rate), 778619 received
  CAN frames (~6MB). Zero new CAN RX/TX errors, retries, bus-offs, dropped
  frames, Klipper retransmissions/invalid bytes or ADXL errors/overflows.
  Both MCUs stayed connected; Pi `throttled=0x0`. Sampling stopped cleanly,
  with Klipper still ready. Results:
  `comms-test-20260913-150946/{baseline,final,result}.json` and checkpoints.
- Test baseline includes pre-test errors (HAT bus-off count 1 and toolhead
  cumulative RX errors 26270); compare counter **deltas**, not just totals.
  The host and toolhead initially had mismatched bitrates before cutover.

Normal config cutover is complete. Reassembled and powered back on 2026-09-13.
Probe hand-trigger check passed at 16:14–16:16 PDT: deployed/untouched = open,
held upward = triggered; user confirmed full retraction after stowing. This
verifies PB9 control and inverted/pulled-up PB8 signal, not nozzle clearance
at the bed or Z calibration.

First supervised `G28` completed at ~16:18 PDT: all axes homed, final Z5,
heaters off, no Klipper retransmits/invalid bytes or disconnects. User confirmed
at 16:20 that the nozzle stopped close to, but did not touch, the bed. **Not a clean
CAN pass:** toolhead RX errors were 131 after startup, rose to 142 on manual
probe deployment, then 164 with a transient warning on stow; homing added
33 more (175 then 197, transient warning). Thus some errors precede motor
motion and align with probe actuation, not just homing. Bus recovered to active
without restart; HAT error-passive event count 2, bus-offs 0. Subsequent UI
Z jog commands raised Z to 106 without further RX errors at the next snapshot.
Defer QGL/stress repetitions pending investigation; do not infer the RP2040
replacement resolved all electrical faults from the stationary-stream pass.

Probe-only isolation at 16:21 PDT reproduced the pattern with XYZ parked at
177.5/177.5/106 and heater targets/power zero: RX errors 197 → 208 after deploy
(+11), then 230 after stow (+22). No Klipper retransmits/invalid bytes, no
TX errors/retries; bus active at the final snapshot. Probe command returned
to stowed. Raw snapshots: `probe-only-20260913-162144.json` in the firmware
archive. This localizes an error trigger to probe actuation/control but does
not distinguish probe hardware, power/ground noise, harness routing or firmware.

Commissioning remains: confirm fan identity, extruder current sense resistor
and direction before the corresponding heating/extrusion tests. Old
`z_offset: 0.240` is not a validated calibration after the probe mount change.
Stationary streaming does not test motor load, heater load or cable flex.

## Manufacturer cross-check and richer diagnostics (2026-09-13)

The [original STM32G0B1 SB2209 schematic](https://github.com/bigtreetech/EBB/blob/master/EBB%20SB2240_2209%20CAN/SB2209/Hardware/BIGTREETECH%20EBB%20SB2209%20CAN%20V1.0_SCH.pdf)
confirms P5 pins 1–5 are GND, fixed 5V, PB9 control, GND, PB8 detection.
PB8 already has R31, a 4.7k pull-up to 3.3V. R53/R55 are 0R11, supporting
`tmc2209 sense_resistor: 0.110`. The probe and CAN transceiver share the board's
5V rail; this is a possible coupling path, not proof of a supply problem.

The [MicroProbe V2 manual](https://github.com/bigtreetech/MicroProbe/blob/master/MicroProbe%20V2%20User%20Manual_20240330.pdf)
specifies 5V power, 350mA operating current, active-low open-drain detection,
3.3V/5V control logic and a 500ms deployment delay. PB9 plus `^!PB8` matches
those requirements. The [issue #19 workaround](https://github.com/bigtreetech/MicroProbe/issues/19#issuecomment-2351699226)
addresses a different RP2040 input circuit; do not add its 10k pull-up blindly.
No matching public report establishing the +11/+22 pattern as a known defect
was found. [Orbitool #16](https://github.com/RobertLorincz/Orbiter-Toolboards/issues/16#issuecomment-2503101765)
contains adjacent reports of probe signal/actuation/repeatability trouble on a
different toolboard, but its designer measured adequate 5V supply under load;
it is not confirmation of this printer's cause.

Detailed HAT error reporting is now enabled with `BusErrorReporting=yes` in
`25-can.network`. `can-error-capture.service` preserves decoded error frames
in the persistent journal. `observability/probe-can-capture.py` saves a finite
raw/decoded capture plus timestamped probe commands and counters in the Pi's
logs directory. See [observability README](../observability/README.md).
These error subtypes are **host-observed**, not a breakdown of the EBB-local
aggregate RX counter. First reconnect failed automated EBB reset; a second
`FIRMWARE_RESTART` recovered readiness, without homing or heating. Homing
status is cleared by this diagnostic restart.

Capture rerun 16:42:43–16:43:12 PDT: toolhead RX 0 → 11 deploy → 33 stow.
The HAT captured **bit-stuffing errors** on both transitions (`20000088`,
`CAN_ERR_PROT | CAN_ERR_BUSERROR`, payload byte 2 = `04`). After stow it
reported RX error-passive (hardware REC 129), warning (127), then recovered
active (94). Five error frames total, no bus-off. These host-reported stuff
errors may include another node's error flag; the initiating node/cause and
EBB-local subtype remain undetermined. Probe returned to stowed; no homing,
gantry motion or heating. Files under `~/printer_data/logs/`:
`can-probe-20260913-164243.{frames.log,errors.log,capture-stderr.log,json,notes.txt}`.
The installed can-utils 2020.11 decoder does not understand combined
`CAN_ERR_CRTL | CAN_ERR_CNT` (`0x204`); its "invalid error class" message is a
decoder limitation. Raw payloads were retained and decoded using Linux headers
in the `.notes.txt` companion. Ongoing error frames remain in the journal.

Protocol decode of that capture found both control packets were correctly
received and application-ACKed ~147ms before the corresponding error. MCU-clock
reconstruction places errors ~50ms after the scheduled PB9 changes, not during
command delivery (not an electrical pin-edge measurement). All 61 command
packets were ACKed; both ADC streams retained their periodic samples. See
`can-probe-20260913-164243.protocol.txt`. Important: STM32 FDCAN's `tx_retries`
field is unpopulated in this firmware, so zero there does not rule out hardware
retries; application acknowledgments/retransmission checks are independent.

**Disconnected-probe control, 17:01 PDT:** user powered off and removed the
MicroProbe connection, then powered on. First attempt stopped at preflight
because Klipper retained its power-cycle shutdown; `FIRMWARE_RESTART` restored
ready. Identical GPIO high/low sequence then produced **zero CAN error frames**
(588 total frames), EBB RX 0 → 0 → 0, no application retransmits/invalid bytes,
and no new HAT error-state/counter events. Output returned to 0; motors and
heaters stayed off. Capture prefix: `~/printer_data/logs/can-probe-20260913-170112`.
The HAT's cumulative bus_error baseline was already 118858 from before this
capture (power-cycle/recovery interval), and stayed flat throughout the test.
This implicates the attached probe/harness/load interaction, not necessarily a
faulty probe alone.

**Reconnected confirmation, 17:17–17:18 PDT:** user confirmed the old external
resistor was not carried over to the new single BLTouch connector, powered off
the toolhead, reconnected the probe, and restored power. After firmware recovery
and waiting for both CAN controllers to return active, the same test reproduced
RX 125 → 136 → 158 (+11 deploy, +22 stow), both HAT bit-stuffing reports, one
HAT RX-passive event and recovery. No bus-off, restart, application retransmit
or invalid-byte increase during capture. Motors/heaters off; probe output 0.
Prefix: `~/printer_data/logs/can-probe-20260913-171742`.
This completes A–B–A: attached fails, disconnected clean, reattached fails.
Probe/input/harness/power-load interaction remains to be separated; this is not
proof that the probe alone is defective. Further motion remains paused.

**Paired input-configuration test, 18:24–18:25 PDT:** attached probe, minimal
`kinematics: none` config with temperature sensors and PB9 digital control.
A included the unchanged `[probe]` PB8 configuration; B removed only that
section. Both reproduced +11 deploy / +22 stow, with HAT stuff-error frames
and transient RX-passive/recovery notifications. Live config snapshots confirm
PB8 probe section present in A and absent in B; PB9 remained digital in both.
This shows Klipper's probe-input handling/sampling is not necessary for the
fault. It does not electrically disconnect PB8 or rule out every firmware or
pin-level interaction. No need for A2 because B did not clear the errors.
Capture prefixes `can-probe-20260913-182408` (A) and
`can-probe-20260913-182443` (B); manifest
`can-probe-input-pair-20260913-182400.json`, all in the Pi logs directory.
The normal config was restored byte-for-byte and runtime-verified corexy;
heaters and motors off, probe output 0, CAN active. Initial test attempts did
not actuate: one was blocked by SSH authentication, another exposed a runner
bug treating expected restart HTTP 503 as fatal. The wait logic now tolerates
503s with a bounded timeout and was tested against transient, permanent and
invalid-config cases before the successful pair.

**White-trigger-lead-disconnected capture, 18:36–18:37 PDT:** user reported
removing the white PB8 sense lead while leaving brown/red/yellow/black connected.
GPIO commands still reproduced RX 124 → 135 → 157 (+11/+22), two HAT stuff-error
reports, one RX-passive event and recovery. No bus-off/restart during capture;
heaters/motors off, output returned to 0. Prefix
`~/printer_data/logs/can-probe-20260913-183642`. A second capture at 18:43,
`can-probe-20260913-184300`, repeated RX 157 → 168 → 190 (+11/+22), and the user
explicitly confirmed the probe extended and retracted normally. Thus removing
the white trigger connection did not prevent either actuation or the error
pattern. This narrows investigation toward power/ground/deploy-control or
internal probe operation, without proving a specific faulty component. Trigger
lead remains disconnected until the user restores it with power off; no homing.

## 0. Before touching hardware — decide bus rate

The G0B1 does 1M cleanly (real CAN controller). Plan: **go back to 1M** — best
bandwidth for ADXL streaming during SHAPER_CALIBRATE. So this swap also reverts
the 500k mitigation:
- `/etc/systemd/network/25-can.network`: `BitRate=500K` → `BitRate=1M`
- Build the G0B1 firmware at `CONFIG_CANBUS_FREQUENCY=1000000`
(If 1M ever looks flaky on the new board, drop both back to 500k — but it won't.)

## 1. Physical swap (power OFF, mains unplugged)

1. Unplug the Stealthburner harness connectors from the old board.
2. Swap the board in the toolhead.
3. Reconnect harness 1:1. **CAN pair to the new board: yellow=H, green=L** (as-built).
4. **120R jumper ON** at the toolhead (still exactly two terminators: HAT + this board).
5. Note which physical port the MicroProbe lands on — it drives the probe pin choice in §4.

## 2. Flash the G0B1 (katapult + Klipper)

The new board ships with USB DFU available. First flash puts katapult on it over
USB, then Klipper over katapult. **Needs the USB cable temporarily** (same drawer
dongle as the Octopus).

Firmware build (`cd ~/klipper && make menuconfig`), or reuse a saved config:
- Enable extra low-level options
- Micro-controller: STMicroelectronics STM32
- Processor model: **STM32G0B1**
- Clock reference: **8 MHz crystal**
- Bootloader offset: **8KiB** (katapult)
- Communication: **CAN bus (on PB0/PB1)**
- CAN bus frequency: **1000000** (per §0)

Katapult build (separate `cd ~/katapult && make menuconfig`): STM32G0B1, 8MHz
crystal, USB (PA11/PA12) or CAN — flash katapult first via USB DFU
(`BOOT0` + USB, or the board's boot button): `make flash FLASH_DEVICE=<DFU id>`.
Then Klipper over katapult USB: `flashtool.py -d /dev/serial/by-id/usb-katapult_* -f ~/klipper/out/klipper.bin`.
Save both binaries + configs to `~/firmware/` as `sb2209-g0b1-*`.

## 3. Get the new UUID + config cutover

New board = new CAN UUID (the old `b129d1ca9b9b` is dead with the old board).

```bash
sudo systemctl stop klipper
flashtool.py -i can0 -q          # prints the new UUID, "Application: Klipper"
```

Then on the Mac repo (or Pi config dir):
1. Put the discovered UUID into `sb2209-g0b1-canbus.cfg.staged` (`REPLACE_AFTER_QUERY`).
2. Rename both staged files: drop `.staged`.
3. `printer.cfg` includes — swap the two lines:
   - `[include rp2040-canbus.cfg]` → `[include sb2209-g0b1-canbus.cfg]`
   - `[include microprobev2.cfg]`  → `[include microprobev2-g0b1.cfg]`
4. Revert bus to 1M (§0), reload networkd or reboot.
5. Deploy to printer, `FIRMWARE_RESTART`.

Expect: klippy **ready**, both MCUs loaded, mini12864 lit.

## 4. Probe verification — MOTION-FREE, before any G28

The two probe pins in `microprobev2-g0b1.cfg` are best-guess (BLTouch-style port:
control=PB9, signal=^!PB8). A wrong signal pin homes into the bed. Verify first:

1. `QUERY_PROBE` → should report `probe: open` with nothing touching it.
2. `SET_PIN PIN=probe_enable VALUE=1` → MicroProbe pin deploys (audible/visible).
3. Hand-press the deployed pin, `QUERY_PROBE` → must flip to `probe: TRIGGERED`.
4. `SET_PIN PIN=probe_enable VALUE=0` → stows.
   - If QUERY_PROBE never changes, or reads TRIGGERED untouched while deployed,
     stop and verify connector pinout, supply, signal conditioning and polarity
     against the schematic. Do not guess alternate pins: PC13 is a separate
     optocoupled proximity input, not an interchangeable BLTouch signal input.
     DO NOT G28 until step 3 passes.

## 5. Only then — the moment of truth

1. `G28` (one careful home — watch Z, hand on E-stop).
2. The 10-cycle QGL loop (`/tmp/qgl_loop.sh`) with candump armed. The RP2040 board
   died in cycle 1 every time. **10 clean cycles = the 13-month bug is dead.**
3. Full Z recal (bracket squares) — owed twice: probe mount moved 09-07 + new board.
4. Then finally: SHAPER_CALIBRATE (ADXL now on hardware SPI), and the print queue
   (rear-panel-clips, bike-guard fit-check, exhaust filter).

## Rollback

Old board's config is untouched in git (`rp2040-canbus.cfg`, `microprobev2.cfg`).
Revert the two `printer.cfg` includes + reflash the old board's uuid to restore.
