#!/usr/bin/env python3
"""PowerPi R3.1 UPS watcher — voron-printer.
Input lost -> grace window (blips ride through on battery) -> clean shutdown.
Battery below VBAT_LOW -> immediate shutdown. BATFET disconnected before halt
so a dead Pi does not drain the cell (input return re-enables it).
Status: journald (1/min + state changes) -> promtail -> Loki/Grafana,
plus /tmp/powerpi_status.json for local/Moonraker consumption."""

import json
import logging
import subprocess
import time

from powerpi import Powerpi

GRACE_SECONDS = 120     # on-battery time before orderly shutdown
POLL_SECONDS = 5        # read_status() itself adds ~2s (ADC conversion)
LOG_EVERY = 12          # ~1 info line per minute

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("powerpi")


def wall(msg):
    subprocess.run(["wall", msg], check=False)


def recover_printer():
    """After printer 24V returns: the EBB rebooted and can0 likely bus-off'd
    or STOPPED while the Pi rode through on battery. Heal both, then restart
    klippy. Idempotent - safe even if nothing was wrong."""
    log.info("printer power returned - waiting for toolhead boot, then recovering CAN + klippy")
    time.sleep(15)
    state = subprocess.run(["ip", "-details", "link", "show", "can0"],
                           capture_output=True, text=True, check=False).stdout
    if "ERROR-ACTIVE" not in state:
        log.warning("can0 not healthy after power return - bouncing interface")
        subprocess.run(["sudo", "ip", "link", "set", "can0", "down"], check=False)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", "can0", "up"], check=False)
        time.sleep(2)
    subprocess.run(["curl", "-s", "-m", "10", "-X", "POST",
                    "http://localhost:7125/printer/firmware_restart"],
                   capture_output=True, check=False)
    log.info("recovery sequence complete (firmware_restart issued)")


def shutdown(ppi, reason):
    log.warning("SHUTDOWN: %s", reason)
    wall("PowerPi UPS: %s - shutting down now" % reason)
    try:
        ppi.bat_disconnect()
    except Exception:
        log.exception("bat_disconnect failed; shutting down anyway")
    subprocess.run(["sudo", "shutdown", "now"], check=False)


def main():
    ppi = Powerpi()
    while ppi.initialize():
        log.error("UPS not reachable on I2C (0x6a) - retrying in 30s")
        time.sleep(30)
    log.info("UPS initialized (BQ25895 @0x6a)")

    on_battery_since = None
    ticks = 0
    while True:
        try:
            err, st = ppi.read_status()
            if err:
                time.sleep(POLL_SECONDS)
                continue
            try:
                with open("/tmp/powerpi_status.json", "w") as f:
                    json.dump(st, f)
            except OSError:
                pass

            pct = st["BatteryPercentage"]
            vbat = st["BatteryVoltage"]
            on_input = st["PowerInputStatus"] == "Connected"

            if not on_input and on_battery_since is None:
                on_battery_since = time.monotonic()
                log.warning("INPUT LOST - on battery (%s%%, %.2fV). Shutdown in %ds unless power returns.",
                            pct, vbat, GRACE_SECONDS)
                wall("PowerPi UPS: input power lost, battery %s%% - shutdown in %ds unless restored"
                     % (pct, GRACE_SECONDS))
            elif on_input and on_battery_since is not None:
                outage = time.monotonic() - on_battery_since
                on_battery_since = None
                log.warning("INPUT RESTORED after %.0fs outage (battery %s%%)", outage, pct)
                wall("PowerPi UPS: power restored after %.0fs (battery %s%%)" % (outage, pct))
                recover_printer()

            if vbat < ppi.VBAT_LOW:
                shutdown(ppi, "battery critically low (%.2fV)" % vbat)
                return
            if on_battery_since is not None and time.monotonic() - on_battery_since >= GRACE_SECONDS:
                shutdown(ppi, "input lost for %ds (battery %s%%)" % (GRACE_SECONDS, pct))
                return

            ticks += 1
            if ticks % LOG_EVERY == 0:
                log.info("status %s", json.dumps(st))
        except Exception:
            # The watcher is a safety function: never die on a transient bug.
            log.exception("watcher loop error; continuing")
            time.sleep(POLL_SECONDS)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
