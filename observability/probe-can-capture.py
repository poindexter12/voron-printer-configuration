#!/usr/bin/env python3
"""Capture one parked MicroProbe cycle; never home, move axes, or heat."""

import argparse
import datetime
import json
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

OBJECTS = {
    "webhooks": None,
    "toolhead": ["homed_axes", "position"],
    "stepper_enable": None,
    "extruder": ["target", "power"],
    "heater_bed": ["target", "power"],
    "output_pin probe_enable": None,
    "canbus_stats EBBCan": None,
    "mcu EBBCan": ["last_stats"],
}
BASE_URL = "http://localhost:7125"


def api(path, data, timeout=10):
    request = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result["result"]


def snapshot(label):
    result = api("/printer/objects/query", {"objects": OBJECTS})
    result["label"] = label
    result["wall_time"] = datetime.datetime.now().astimezone().isoformat()
    result["can_interface"] = json.loads(subprocess.check_output(
        ["ip", "-json", "-details", "-statistics", "link", "show", "can0"],
        timeout=10,
    ))[0]
    return result


def assert_safe(record, sensor_only=False):
    status = record["status"]
    if status["webhooks"]["state"] != "ready":
        raise RuntimeError("Klipper is not ready")
    if sensor_only:
        config = api("/printer/objects/query", {
            "objects": {"configfile": ["config", "settings"]}
        })["status"]["configfile"]
        allowed = {
            "mcu", "mcu ebbcan", "printer", "output_pin probe_enable",
            "temperature_sensor toolhead_hotend", "temperature_sensor ebb_ntc",
            "temperature_sensor toolhead_mcu", "probe",
            "gcode_macro _probe_deploy", "gcode_macro _probe_stow",
        }
        if set(name.lower() for name in config["config"]) - allowed:
            raise RuntimeError("Unexpected sections in sensor-only configuration")
        if config["settings"]["printer"]["kinematics"] != "none":
            raise RuntimeError("Sensor-only test requires kinematics: none")
        pin = config["settings"]["output_pin probe_enable"]
        if pin["pin"] != "EBBCan:PB9" or pin["pwm"]:
            raise RuntimeError("Sensor-only test requires digital probe control on PB9")
        record["configuration"] = config
    else:
        for heater in ("extruder", "heater_bed"):
            if status[heater]["target"] or status[heater]["power"]:
                raise RuntimeError("Heaters must be off")
        if any(status["stepper_enable"]["steppers"].values()):
            raise RuntimeError("Motors must already be disabled for this test")
    if status["canbus_stats EBBCan"]["bus_state"] != "active":
        raise RuntimeError("CAN must be active before testing")
    if status["output_pin probe_enable"]["value"]:
        raise RuntimeError("Probe must initially be stowed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clearance-confirmed", action="store_true",
                        help="Operator verified at least 10mm physical probe clearance")
    parser.add_argument("--sensor-only", action="store_true",
                        help="Require a restricted diagnostic config with no motion/heaters")
    parser.add_argument("--condition", default="unspecified",
                        help="Describe the wiring/configuration condition in the capture")
    args = parser.parse_args()
    if not args.clearance_confirmed:
        parser.error("Verify physical clearance, then pass --clearance-confirmed")

    directory = Path.home() / "printer_data/logs"
    prefix = directory / ("can-probe-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    paths = {name: Path(str(prefix) + suffix) for name, suffix in {
        "raw": ".frames.log", "errors": ".errors.log", "stderr": ".capture-stderr.log",
        "metadata": ".json",
    }.items()}
    metadata = {"started": datetime.datetime.now().astimezone().isoformat(),
                "observer": "Pi MCP2518FD HAT; not toolhead-local error subtypes",
                "condition": args.condition, "sensor_only": args.sensor_only,
                "snapshots": [], "commands": [], "failure": None}
    processes = []
    streams = []
    deployed = False

    def record(label):
        item = snapshot(label)
        metadata["snapshots"].append(item)
        print(label, json.dumps(item["status"]["canbus_stats EBBCan"]), flush=True)
        return item

    def command(script):
        metadata["commands"].append({"wall_time": time.time(), "script": script})
        return api("/printer/gcode/script", {"script": script}, timeout=30)

    try:
        metadata["snapshots"].append(snapshot("preflight"))
        assert_safe(metadata["snapshots"][-1], args.sensor_only)
        stderr = paths["stderr"].open("x")
        streams.append(stderr)
        for name, options, can_filter in (
            ("raw", ["-L", "-d"], "can0,0:0,#FFFFFFFF"),
            ("errors", ["-t", "A", "-e", "-x", "-d"], "can0,0~0,#FFFFFFFF"),
        ):
            output = paths[name].open("x")
            streams.append(output)
            processes.append(subprocess.Popen(
                ["stdbuf", "-oL", "candump", *options, can_filter],
                stdout=output, stderr=stderr,
            ))
        print("CAPTURE_PREFIX=" + str(prefix), flush=True)
        command("G4 P6000")
        if any(process.poll() is not None for process in processes):
            raise RuntimeError("CAN capture process exited before actuation")
        assert_safe(record("before_deploy"), args.sensor_only)
        deployed = True  # Also attempt stow if the deployment request times out.
        command("SET_PIN PIN=probe_enable VALUE=1\nG4 P8000")
        record("deployed_8s")
        command("SET_PIN PIN=probe_enable VALUE=0\nG4 P16000")
        deployed = False
        record("stowed_16s")
        if any(process.poll() is not None for process in processes):
            raise RuntimeError("CAN capture process exited during the test")
    except Exception as exc:
        metadata["failure"] = str(exc)
    finally:
        if deployed:
            try:
                command("SET_PIN PIN=probe_enable VALUE=0")
            except Exception as exc:
                metadata["stow_failure"] = str(exc)
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for stream in streams:
            stream.close()
        metadata["finished"] = datetime.datetime.now().astimezone().isoformat()
        metadata["files"] = {key: str(value) for key, value in paths.items()
                             if value.exists() or key == "metadata"}
        with paths["metadata"].open("x") as output:
            json.dump(metadata, output, indent=2)
        print(json.dumps({"failure": metadata["failure"], "files": metadata["files"]}), flush=True)
    return 1 if metadata["failure"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
