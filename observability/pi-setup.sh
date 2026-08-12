#!/usr/bin/env bash
# Install prometheus-klipper-exporter + promtail on the printer Pi.
# Run ON the Pi (or: ssh trusted.voron-printer.home.arpa 'bash -s' < pi-setup.sh)
set -euo pipefail

# IMPORTANT: use USERLAND arch (dpkg), not kernel arch (uname) — this Pi runs an
# aarch64 kernel over an armhf userland; dynamically-linked arm64 binaries fail
# there with a misleading ENOENT (missing aarch64 loader).
ARCH=$(dpkg --print-architecture 2>/dev/null || uname -m)
case "$ARCH" in
  arm64|aarch64) GOARCH=arm64 ;;
  armhf|armv7l)  GOARCH=arm ;;
  amd64|x86_64)  GOARCH=amd64 ;;
  *) echo "unsupported arch $ARCH"; exit 1 ;;
esac

# --- prometheus-klipper-exporter (bare binary assets, rpi-* flavor for Pi) ---
KVER=$(curl -s https://api.github.com/repos/scross01/prometheus-klipper-exporter/releases/latest | grep -oP '"tag_name": "\K[^"]+')
case "$ARCH" in
  aarch64) KASSET="prometheus-klipper-exporter-rpi-arm64-${KVER}" ;;
  armv7l)  KASSET="prometheus-klipper-exporter-rpi-armv7-${KVER}" ;;
  *)       KASSET="prometheus-klipper-exporter-linux-${GOARCH}-${KVER}" ;;
esac
echo "installing klipper-exporter ${KVER} (${KASSET})"
sudo mkdir -p /opt/klipper-exporter
sudo curl -sL -o /opt/klipper-exporter/prometheus-klipper-exporter "https://github.com/scross01/prometheus-klipper-exporter/releases/download/${KVER}/${KASSET}"
sudo chmod +x /opt/klipper-exporter/prometheus-klipper-exporter

sudo tee /etc/systemd/system/klipper-exporter.service >/dev/null <<'UNIT'
[Unit]
Description=Prometheus Klipper Exporter
After=network-online.target moonraker.service
Wants=network-online.target

[Service]
ExecStart=/opt/klipper-exporter/prometheus-klipper-exporter -moonraker.apikey "" -web.listen-address :9101
Restart=always
RestartSec=5
User=nobody

[Install]
WantedBy=multi-user.target
UNIT

# --- promtail ---
# promtail is deprecated upstream; v3.4.5 is the last release shipping binaries.
# Works fine against Loki 3.x servers. Successor: Grafana Alloy (migrate someday).
PVER=v3.4.5
echo "installing promtail ${PVER} (${GOARCH})"
curl -sL -o /tmp/promtail.zip "https://github.com/grafana/loki/releases/download/${PVER}/promtail-linux-${GOARCH}.zip"
sudo apt-get install -y -qq unzip >/dev/null 2>&1 || true
sudo unzip -o -q /tmp/promtail.zip -d /opt/promtail
sudo mv "/opt/promtail/promtail-linux-${GOARCH}" /opt/promtail/promtail 2>/dev/null || true
sudo chmod +x /opt/promtail/promtail
sudo mkdir -p /etc/promtail /var/lib/promtail
# config is deployed alongside this script
sudo cp "$(dirname "$0")/promtail-config.yml" /etc/promtail/config.yml 2>/dev/null || \
  echo "NOTE: copy promtail-config.yml to /etc/promtail/config.yml manually"

sudo tee /etc/systemd/system/promtail.service >/dev/null <<'UNIT'
[Unit]
Description=Promtail log shipper
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/opt/promtail/promtail -config.file /etc/promtail/config.yml
Restart=always
RestartSec=5
# journal access:
SupplementaryGroups=systemd-journal adm

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now klipper-exporter promtail
sleep 3
echo "--- verify ---"
curl -s localhost:9101/metrics | head -3 || echo "exporter not answering"
systemctl is-active klipper-exporter promtail
