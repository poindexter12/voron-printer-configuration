#!/usr/bin/env bash
# Install prometheus-klipper-exporter + promtail on the printer Pi.
# Run ON the Pi (or: ssh trusted.voron-printer.home.arpa 'bash -s' < pi-setup.sh)
set -euo pipefail

ARCH=$(uname -m)
case "$ARCH" in
  aarch64) GOARCH=arm64 ;;
  armv7l)  GOARCH=arm ;;
  x86_64)  GOARCH=amd64 ;;
  *) echo "unsupported arch $ARCH"; exit 1 ;;
esac

# --- prometheus-klipper-exporter ---
KVER=$(curl -s https://api.github.com/repos/scross01/prometheus-klipper-exporter/releases/latest | grep -oP '"tag_name": "\K[^"]+')
echo "installing klipper-exporter ${KVER} (${GOARCH})"
curl -sL -o /tmp/kexp.tar.gz "https://github.com/scross01/prometheus-klipper-exporter/releases/download/${KVER}/prometheus-klipper-exporter_${KVER#v}_linux_${GOARCH}.tar.gz"
sudo mkdir -p /opt/klipper-exporter
sudo tar -xzf /tmp/kexp.tar.gz -C /opt/klipper-exporter

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
PVER=$(curl -s https://api.github.com/repos/grafana/loki/releases/latest | grep -oP '"tag_name": "\K[^"]+')
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
