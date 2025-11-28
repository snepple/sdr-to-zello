#!/usr/bin/env python3
import json
import os
import sys
import shutil
from typing import Any, Callable

# This is the config file that is READ and WRITTEN
CFG_PATH = "/data/configs/trunk-recorder.json"
MAX_SDR_DEVICES = 5  # New constant for max devices

def load_config(path: str) -> Any:
    try:
        # On first boot, this file might not exist,
        # so we check for the /app/ version as a fallback.
        base_config_path = "/app/configs/trunk-recorder.json"
        
        load_path = path
        if not os.path.exists(path) and os.path.exists(base_config_path):
            print(f"Config file {path} not found. Loading from base config {base_config_path}.")
            load_path = base_config_path
        
        with open(load_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"Config file {path} and base config {base_config_path} not found. Skipping overrides.")
        return None
    except json.JSONDecodeError as exc:
        print(f"Unable to parse {path}: {exc}")
        return None

def write_config(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def set_env(cfg: Any, env: str, setter: Callable[[str], None]) -> None:
    raw = os.getenv(env)
    if raw is None or raw == "":
        return
    try:
        setter(raw)
    except ValueError as exc:
        print(f"Skipping {env}: {exc}")


def coerce_int(raw: str, field: str, allow_float: bool = False) -> int:
    value = float(raw) if allow_float else int(raw)
    return int(value)


def main() -> int:
    cfg = load_config(CFG_PATH)
    if cfg is None:
        return 0

    # Ensure sources list exists
    sources = cfg.get("sources") or []
    cfg["sources"] = sources

    # --- Multiple SDR Source Overrides ---
    for i in range(1, MAX_SDR_DEVICES + 1):
        center_env = f"SDR_{i}_CENTER_HZ"
        raw_center = os.getenv(center_env)
        
        if raw_center is not None and raw_center.strip() != "":
            print(f"--- Configuring SDR Source {i} (from {center_env}) ---")

            if len(sources) < i:
                new_source = {
                    "center": 100000000, 
                    "rate": 2048000,     
                    "driver": "osmosdr",   
                    "device": f"rtl={i - 1}", 
                    "index": i - 1        
                }
                sources.append(new_source)

            source = sources[i - 1]
            source.__setitem__("index", i - 1)
            if "driver" not in source: source.__setitem__("driver", "osmosdr")
            if "device" not in source: source.__setitem__("device", f"rtl={i - 1}")

            set_env(cfg, center_env, lambda raw: source.__setitem__("center", coerce_int(raw, "center", allow_float=True)))
            set_env(cfg, f"SDR_{i}_SAMPLE_RATE", lambda raw: source.__setitem__("rate", coerce_int(raw, "rate", allow_float=True)))
            set_env(cfg, f"SDR_{i}_ERROR_HZ", lambda raw: source.__setitem__("error", coerce_int(raw, "error", allow_float=True)))
            set_env(cfg, f"SDR_{i}_GAIN_DB", lambda raw: source.__setitem__("gain", coerce_int(raw, "gain", allow_float=True)))
            set_env(cfg, f"SDR_{i}_SIGNAL_DETECTOR_THRESHOLD", lambda raw: source.__setitem__("signalDetectorThreshold", coerce_int(raw, "signalDetectorThreshold", allow_float=True)))
        
        # --- Backwards Compatibility for SDR 1 ---
        elif i == 1 and os.getenv("TR_CENTER_HZ") is not None and os.getenv("TR_CENTER_HZ").strip() != "":
            print("--- Configuring SDR Source 1 (from legacy TR_CENTER_HZ) ---")
            source = sources[0] if sources else {"center": 100000000, "rate": 2048000, "index": 0, "driver": "osmosdr", "device": "rtl=0"}
            if not sources: sources.append(source)
            set_env(cfg, "TR_CENTER_HZ", lambda raw: source.__setitem__("center", coerce_int(raw, "center", allow_float=True)))
            set_env(cfg, "TR_SAMPLE_RATE", lambda raw: source.__setitem__("rate", coerce_int(raw, "rate", allow_float=True)))
            set_env(cfg, "TR_ERROR_HZ", lambda raw: source.__setitem__("error", coerce_int(raw, "error", allow_float=True)))
            set_env(cfg, "TR_GAIN_DB", lambda raw: source.__setitem__("gain", coerce_int(raw, "gain", allow_float=True)))
            set_env(cfg, "TR_SIGNAL_DETECTOR_THRESHOLD", lambda raw: source.__setitem__("signalDetectorThreshold", coerce_int(raw, "signalDetectorThreshold", allow_float=True)))


    # --- System Overrides ---
    systems = cfg.get("systems") or []
    system = systems[0] if systems else None
    if system:
        set_env(cfg, "TR_SQUELCH_DB", lambda raw: system.__setitem__("squelch", int(float(raw))))
        
        raw_channel_file = os.getenv("TR_CHANNEL_FILE")
        raw_channels_hz = os.getenv("TR_CHANNELS_HZ")

        if raw_channel_file is not None and raw_channel_file.strip() != "":
            print("\n--- Copying Channel File ---")
            filename = raw_channel_file.strip()
            source_path = f"/app/configs/{filename}"
            dest_path = f"/app/{filename}"
            try:
                if not os.path.exists(source_path):
                    print(f"CRITICAL: Source file not found at {source_path}.")
                else:
                    shutil.copy(source_path, dest_path)
                    print("File copy SUCCEEDED.")
            except Exception as e:
                print(f"CRITICAL: File copy FAILED. Error: {e}")

            system["channelFile"] = filename
            system.pop('channels', None)
            system.pop('control_channels', None) 
            
        elif raw_channels_hz is not None and raw_channels_hz.strip() != "":
            try:
                parts = [part.strip() for part in raw_channels_hz.split(",") if part.strip()]
                frequency_list = [int(float(part)) for part in parts]
                system["channels"] = frequency_list
                system["control_channels"] = frequency_list
                system.pop('channelFile', None)
            except ValueError as exc:
                print(f"Skipping TR_CHANNELS_HZ: {exc}")

        set_env(cfg, "TR_ANALOG_LEVELS", lambda raw: system.__setitem__("AnalogLevels", coerce_int(raw, "AnalogLevels", allow_float=True)))
        set_env(cfg, "TR_DIGITAL_LEVELS", lambda raw: system.__setitem__("DigitalLevels", coerce_int(raw, "DigitalLevels", allow_float=True)))
        set_env(cfg, "TR_SYSTEM_TYPE", lambda raw: system.__setitem__("type", raw.strip()))
        
        raw_mod = os.getenv("TR_SYSTEM_MODULATION")
        if raw_mod is not None and raw_mod.strip() != "":
             system["modulation"] = raw_mod.strip()
        else:
             system.pop("modulation", None)

    # --- Plugin Overrides (With toggle to DISABLE streaming) ---
    # If TR_ENABLE_STREAMING is set to "false", we remove the simplestream plugin.
    enable_streaming = os.getenv("TR_ENABLE_STREAMING", "true").lower() == "true"
    
    if "plugins" in cfg:
        # Filter out simplestream if streaming is disabled
        if not enable_streaming:
            print("--- Streaming Disabled (TR_ENABLE_STREAMING=false). Removing simplestream plugin. ---")
            cfg["plugins"] = [p for p in cfg["plugins"] if p.get("name") != "simplestream"]
        
        # Configure if still present
        plugins = cfg.get("plugins", [])
        stream_plugin = next((p for p in plugins if p.get("name") == "simplestream"), None)
        
        if stream_plugin:
            streams = stream_plugin.get("streams") or []
            stream = streams[0] if streams else None
            if stream:
                set_env(cfg, "TR_PLUGIN_PORT", lambda raw: stream.__setitem__("port", coerce_int(raw, "port")))
                set_env(cfg, "TR_PLUGIN_ADDRESS", lambda raw: stream.__setitem__("address", raw.strip()))
                set_env(cfg, "TR_PLUGIN_TGID", lambda raw: stream.__setitem__("TGID", int(raw, 0)))
                set_env(cfg, "TR_PLUGIN_SEND_JSON", lambda raw: stream.__setitem__("sendJSON", raw.strip().lower() in {"1", "true", "yes"}))
        else:
            print("Simplestream plugin not found or removed.")
    else:
        print("No plugins configured.")

    write_config(CFG_PATH, cfg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
