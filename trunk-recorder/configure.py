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
    # If the environment variable is a float (e.g., 25000000.0), this handles it.
    value = float(raw) if allow_float else int(raw)
    # The return value should be int for frequency/rate settings
    return int(value)


def main() -> int:
    cfg = load_config(CFG_PATH)
    if cfg is None:
        return 0

    # Ensure sources list exists
    sources = cfg.get("sources") or []
    cfg["sources"] = sources

    # --- Multiple SDR Source Overrides ---
    # Loop through up to MAX_SDR_DEVICES (1 to 5)
    for i in range(1, MAX_SDR_DEVICES + 1):
        # The key environment variable to check for existence
        center_env = f"SDR_{i}_CENTER_HZ"
        
        raw_center = os.getenv(center_env)
        
        # Only process if a center frequency is specified for this index
        if raw_center is not None and raw_center.strip() != "":
            print(f"--- Configuring SDR Source {i} (from {center_env}) ---")

            # 1. Get or create the source object in the list
            if len(sources) < i:
                # CORRECTED: Create new source with required driver and device keys
                new_source = {
                    "center": 100000000, # Placeholder/Default
                    "rate": 2048000,     # Placeholder/Default
                    "driver": "osmosdr",   
                    "device": f"rtl={i - 1}", # rtl=0, rtl=1, etc.
                    "index": i - 1       
                }
                sources.append(new_source)

            # Get the source reference for update
            source = sources[i - 1]
            
            # Ensure the source has a 0-based index set
            source.__setitem__("index", i - 1)
            
            # Ensure the source has the driver set for existing sources that are updated
            if "driver" not in source:
                 source.__setitem__("driver", "osmosdr")
                 
            if "device" not in source:
                 source.__setitem__("device", f"rtl={i - 1}")


            # 2. Apply all settings using the new indexed environment variable names
            
            # CENTER FREQUENCY (Required to trigger configuration)
            set_env(
                cfg,
                center_env,
                lambda raw: source.__setitem__("center", coerce_int(raw, "center", allow_float=True)),
            )

            # SAMPLE RATE
            set_env(
                cfg,
                f"SDR_{i}_SAMPLE_RATE",
                lambda raw: source.__setitem__("rate", coerce_int(raw, "rate", allow_float=True)),
            )

            # FREQUENCY ERROR
            set_env(
                cfg,
                f"SDR_{i}_ERROR_HZ",
                lambda raw: source.__setitem__("error", coerce_int(raw, "error", allow_float=True)),
            )

            # GAIN
            set_env(
                cfg,
                f"SDR_{i}_GAIN_DB",
                lambda raw: source.__setitem__("gain", coerce_int(raw, "gain", allow_float=True)),
            )

            # SIGNAL DETECTOR THRESHOLD
            set_env(
                cfg,
                f"SDR_{i}_SIGNAL_DETECTOR_THRESHOLD",
                lambda raw: source.__setitem__("signalDetectorThreshold", coerce_int(raw, "signalDetectorThreshold", allow_float=True)),
            )
        
        # --- Backwards Compatibility for SDR 1 (TR_...) ---
        elif i == 1 and os.getenv("TR_CENTER_HZ") is not None and os.getenv("TR_CENTER_HZ").strip() != "":
            print("--- Configuring SDR Source 1 (from legacy TR_CENTER_HZ) ---")
            
            # Ensure source 1 exists
            source = sources[0] if sources else {
                "center": 100000000, 
                "rate": 2048000, 
                "index": 0,
                "driver": "osmosdr",   
                "device": "rtl=0"      
            }
            if not sources:
                 sources.append(source)
                 
            # Re-apply original logic for backwards compatibility
            set_env(
                cfg,
                "TR_CENTER_HZ",
                lambda raw: source.__setitem__("center", coerce_int(raw, "center", allow_float=True)),
            )
            set_env(
                cfg,
                "TR_SAMPLE_RATE",
                lambda raw: source.__setitem__("rate", coerce_int(raw, "rate", allow_float=True)),
            )
            set_env(
                cfg,
                "TR_ERROR_HZ",
                lambda raw: source.__setitem__("error", coerce_int(raw, "error", allow_float=True)),
            )
            set_env(
                cfg,
                "TR_GAIN_DB",
                lambda raw: source.__setitem__("gain", coerce_int(raw, "gain", allow_float=True)),
            )
            set_env(
                cfg,
                "TR_SIGNAL_DETECTOR_THRESHOLD",
                lambda raw: source.__setitem__("signalDetectorThreshold", coerce_int(raw, "signalDetectorThreshold", allow_float=True)),
            )


    # --- System and Plugin Overrides (Unchanged Logic) ---
    systems = cfg.get("systems") or []
    system = systems[0] if systems else None
    if system is None:
        print("No systems defined; skipping system overrides.")
    else:
        set_env(
            cfg,
            "TR_SQUELCH_DB",
            lambda raw: system.__setitem__("squelch", int(float(raw))),
        )
        
        # <<< FINALIZED SECTION FOR CHANNEL/CHANNELFILE >>>
        
        raw_channel_file = os.getenv("TR_CHANNEL_FILE")
        raw_channels_hz = os.getenv("TR_CHANNELS_HZ")

        if raw_channel_file is not None and raw_channel_file.strip() != "":
            
            print("\n--- Copying Channel File ---")
            
            filename = raw_channel_file.strip()
            source_path = f"/app/configs/{filename}"
            dest_path = f"/app/{filename}"

            print(f"Source file (from repo): {source_path}")
            print(f"Destination file (for runtime): {dest_path}")

            try:
                if not os.path.exists(source_path):
                    print(f"CRITICAL: Source file not found at {source_path}. Ensure it's in your 'configs' dir in Git.")
                else:
                    shutil.copy(source_path, dest_path)
                    print("File copy SUCCEEDED.")
            except Exception as e:
                print(f"CRITICAL: File copy FAILED. Error: {e}")

            system["channelFile"] = filename
            system.pop('channels', None)
            # Remove control_channels if using a channel file
            system.pop('control_channels', None) 
            print(f"Set JSON 'channelFile' to: {filename}")
            print("--- End Channel File ---")

            
        elif raw_channels_hz is not None and raw_channels_hz.strip() != "":
            try:
                parts = [part.strip() for part in raw_channels_hz.split(",") if part.strip()]
                if not parts:
                    raise ValueError("no values supplied for TR_CHANNELS_HZ")
                
                frequency_list = [int(float(part)) for part in parts]
                
                # --- FIX: Set both 'channels' and 'control_channels' to prevent JSON type errors ---
                system["channels"] = frequency_list
                system["control_channels"] = frequency_list
                
                system.pop('channelFile', None)
                print(f"Using TR_CHANNELS_HZ. Setting 'channels' and 'control_channels'. Removing 'channelFile' key.")
            except ValueError as exc:
                print(f"Skipping TR_CHANNELS_HZ: {exc}")

        set_env(
            cfg,
            "TR_ANALOG_LEVELS",
            lambda raw: system.__setitem__("AnalogLevels", coerce_int(raw, "AnalogLevels", allow_float=True)),
        )
        set_env(
            cfg,
            "TR_DIGITAL_LEVELS",
            lambda raw: system.__setitem__("DigitalLevels", coerce_int(raw, "DigitalLevels", allow_float=True)),
        )
        set_env(
            cfg,
            "TR_SYSTEM_TYPE",
            lambda raw: system.__setitem__("type", raw.strip()),
        )
        set_env(
            cfg,
            "TR_SYSTEM_MODULATION",
            lambda raw: system.__setitem__("modulation", raw.strip()),
        )

    # ... (rest of plugin logic) ...
    plugins = cfg.get("plugins") or []
    if plugins:
        plugin = plugins[0]
        streams = plugin.get("streams") or []
        stream = streams[0] if streams else None
        if stream:
            set_env(
                cfg,
                "TR_PLUGIN_PORT",
                lambda raw: stream.__setitem__("port", coerce_int(raw, "port")),
            )
            set_env(
                cfg,
                "TR_PLUGIN_ADDRESS",
                lambda raw: stream.__setitem__("address", raw.strip()),
            )
            set_env(
                cfg,
                "TR_PLUGIN_TGID",
                lambda raw: stream.__setitem__("TGID", int(raw, 0)),
            )
            set_env(
                cfg,
                "TR_PLUGIN_SEND_JSON",
                lambda raw: stream.__setitem__("sendJSON", raw.strip().lower() in {"1", "true", "yes"}),
            )
    else:
        print("No plugins configured; skipping plugin overrides.")

    write_config(CFG_PATH, cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
