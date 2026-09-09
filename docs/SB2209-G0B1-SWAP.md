# SB2209 Toolhead Swap: RP2040 → STM32G0B1

Replacing the SB2209 CAN **RP2040** board (convicted 2026-09-07: its can2040
software CAN bus-offs under ANY motion — see project memory) with the SB2209
CAN V1.0 **STM32G0B1** board (hardware FDCAN). Same form factor, same
Stealthburner wiring harness — the toolhead-side connectors move over 1:1.

Staged config already written (drop the `.staged` suffix at cutover):
- `config/sb2209-g0b1-canbus.cfg.staged`  (toolhead hardware, G0B1 pins)
- `config/microprobev2-g0b1.cfg.staged`   (probe, G0B1 pins — VERIFY before homing)

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
   - If QUERY_PROBE never changes, or reads TRIGGERED untouched → wrong signal
     pin or polarity. Fix `[probe] pin:` (try `^PC13`, or check the board IO PDF)
     and repeat. DO NOT G28 until step 3 passes.

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
