# Printer observability

Ships printer metrics + logs to the homelab stack at metrics.home.arpa
(Prometheus :9090, Loki :3100, Grafana :3000 — dashboard uid `voron-printer`).

- `pi-setup.sh` — run ON the printer Pi. Installs prometheus-klipper-exporter
  (:9101) and promtail (journal + klippy.log -> Loki) as systemd services.
- `promtail-config.yml` — deployed by pi-setup.sh to /etc/promtail/config.yml.
- `prometheus-scrape.yml` — snippet to add to the obs host's prometheus.yml
  scrape_configs (managed in the observability stack's own repo/session).

## CAN error subtypes

`can-error-capture.service` preserves decoded SocketCAN error frames from the
MCP2518FD HAT in the persistent system journal. It receives only error frames;
ordinary printer traffic is excluded. `powerpi/25-can.network` must include
`BusErrorReporting=yes` to enable the driver's detailed error reports. This was
enabled on the printer on 2026-09-13. It does not modify bus speed or termination.

On the Pi:

```bash
journalctl -u can-error-capture.service --since today
journalctl -fu can-error-capture.service
```

Install the unit at `/etc/systemd/system/can-error-capture.service`, then run
`sudo systemctl daemon-reload` and
`sudo systemctl enable --now can-error-capture.service`. The unit uses the
printer's `poindexter12` account and requires `can-utils`. Journal retention is
bounded by the Pi's existing journald policy, not indefinite archival.

### One probe-only capture

`probe-can-capture.py` records one deploy/stow cycle with timestamps, raw CAN
traffic, decoded CAN errors and Klipper counter snapshots. It does **not** home,
move axes or heat. It requires Klipper ready, both heaters off, all motors already
disabled and the probe initially stowed. The operator must verify physical
clearance of at least 10mm; software cannot verify clearance after a restart.

```bash
python3 probe-can-capture.py --clearance-confirmed --condition "probe attached, normal config"
```

For the paired input-mode experiment, `--sensor-only` requires a strict
allowlist of diagnostic config sections and `kinematics: none`, rather than
requiring heater/motor objects that intentionally do not exist. It verifies
PB9 is ordinary digital control, and saves the live config with the snapshots.
It does not install that config or change wiring. Do not use it with the normal
printer config. `--condition` labels the wiring/configuration tested; it changes
no behavior.

Output files are under `~/printer_data/logs/can-probe-<timestamp>`:

- `.frames.log`: all data and error frames, original CAN IDs/payloads/timestamps.
- `.errors.log`: decoded error frames (stuff/form/CRC/ACK/bit errors when reported).
- `.json`: timestamped commands, counter snapshots and any test failure.
- `.capture-stderr.log`: capture-process diagnostics.

These files are accessible through Moonraker's logs root. Captures are finite
and remain until removed; they are not automatically rotated by this script.
No explicit pass/fail judgment about CAN quality is made: inspect the counters
and captures even when the script exits successfully.

**Observer limitation:** these are errors detected by the **Pi's CAN HAT**.
They are not a per-subtype breakdown of the EBB's `rx_error` counter, and one
host error frame may combine several flags. Stock Klipper's STM32 FDCAN code
aggregates receive last-error codes rather than logging each subtype. An empty
host error log does not disprove an EBB-local error; obtaining that side may
require instrumented MCU firmware.

The Pi's can-utils 2020.11 decoder reports "Error class 0x204 is invalid" for
newer combined `CAN_ERR_CRTL | CAN_ERR_CNT` status frames. Their raw payloads
are still preserved. In those frames, byte 1 contains controller state flags
and bytes 6/7 contain TX/RX hardware error counters; use the current Linux
`can/error.h` definitions when decoding. This decoder warning is not another
bus fault. Bit-stuffing errors are decoded correctly by this version.

Enabling reporting on a running interface requires a link reconfiguration and
may interrupt Klipper. Do this only with the printer idle and heaters off,
recover the connection, and verify readiness before testing. Do not home just
to satisfy a diagnostic precondition.
