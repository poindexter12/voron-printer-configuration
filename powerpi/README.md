# PowerPi R3.1 UPS — Pi-side tooling

Deployed on the printer Pi at `~/powerpi/` (service installed to
`/etc/systemd/system/powerpi-ups.service`, enabled). This dir is the
versioned source of truth — the Pi copy lives outside printer_data and is
NOT covered by the hourly autocommit.

- `powerpi.py` — driver from tjohn327/raspberry_pi_ups (BQ25895 @ I2C 0x6a),
  charge current capped at 0.5A for the 5V input budget
- `ups_watcher.py` — input-loss watcher: 120s grace → BATFET disconnect →
  clean shutdown; auto-recovery on power return (bounce can0 + firmware_restart);
  telemetry to journald (→ Loki) + /tmp/powerpi_status.json
- `powerpi-ups.service` — systemd unit (User=poindexter12, passwordless sudo)
- `25-can.network` — /etc/systemd/network/ config for the CAN HAT
  (RestartSec=100ms bus-off auto-recovery; BitRate matches EBB firmware —
  500K during the RP2040 mitigation era, back to 1M with the G0B1 board)

Redeploy: scp files, `sudo cp powerpi-ups.service /etc/systemd/system/`,
`sudo systemctl daemon-reload && sudo systemctl enable --now powerpi-ups`.
Full context: docs/POWER-AND-SHUTDOWN.md.
