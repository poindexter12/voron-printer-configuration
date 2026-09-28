#!/usr/bin/env python3
"""Drive the printer through Moonraker's HTTP API (works when SSH does not).

Usage:
  moonraker.py status                  state, temps, homed axes, gcode offset
  moonraker.py gcode "G28" ["M400"]    run G-code, one argument per line
  moonraker.py upload FILE [--config]  upload to gcodes/ (or config/)
  moonraker.py start NAME              start a print already on the printer
  moonraker.py cancel
  moonraker.py log [N]                 last N console lines (default 30)
  moonraker.py restart                 Klipper config restart

Nothing here checks that the bed is clear: moving or heating the printer
still needs a human go-ahead first.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
import uuid

BASE = os.environ.get("MOONRAKER", "http://voron-printer.home.arpa:7125")


def call(path, body=None, timeout=900):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method="GET" if body is None else "POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)["result"]


def upload(path, root):
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    with open(path, "rb") as f:
        payload = f.read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"root\"\r\n\r\n{root}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n").encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/server/files/upload", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def status():
    q = ("print_stats&extruder=temperature,target&heater_bed=temperature,target"
         "&toolhead=homed_axes,position&gcode_move=homing_origin")
    s = call(f"/printer/objects/query?{q}")["status"]
    ps, ex, bed, th = s["print_stats"], s["extruder"], s["heater_bed"], s["toolhead"]
    print(f"{ps['state']:<9} {ps.get('filename') or '-'}")
    print(f"nozzle {ex['temperature']:.1f}/{ex['target']:.0f}  bed {bed['temperature']:.1f}/{bed['target']:.0f}")
    print(f"homed '{th['homed_axes']}'  pos {[round(p, 2) for p in th['position'][:3]]}  "
          f"z offset {s['gcode_move']['homing_origin'][2]:+.3f}")


def main(argv):
    cmd, args = (argv[0], argv[1:]) if argv else ("status", [])
    if cmd == "status":
        status()
    elif cmd == "gcode":
        call("/printer/gcode/script", {"script": "\n".join(args)})
    elif cmd == "upload":
        print(upload(args[0], "config" if "--config" in args else "gcodes")["item"]["path"])
    elif cmd == "start":
        call("/printer/print/start?filename=" + urllib.parse.quote(args[0]), {})
    elif cmd == "cancel":
        call("/printer/print/cancel", {})
    elif cmd == "log":
        n = int(args[0]) if args else 30
        for m in call(f"/server/gcode_store?count={n}")["gcode_store"]:
            print(m["message"])
    elif cmd == "restart":
        call("/printer/restart", {})
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
