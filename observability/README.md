# Printer observability

Ships printer metrics + logs to the homelab stack at metrics.home.arpa
(Prometheus :9090, Loki :3100, Grafana :3000 — dashboard uid `voron-printer`).

- `pi-setup.sh` — run ON the printer Pi. Installs prometheus-klipper-exporter
  (:9101) and promtail (journal + klippy.log -> Loki) as systemd services.
- `promtail-config.yml` — deployed by pi-setup.sh to /etc/promtail/config.yml.
- `prometheus-scrape.yml` — snippet to add to the obs host's prometheus.yml
  scrape_configs (managed in the observability stack's own repo/session).
