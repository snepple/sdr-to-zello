#!/usr/bin/env python3
import json
import os
import sys
import shutil
from typing import Any, Callable

CFG_PATH = "/data/configs/trunk-recorder.json"

def load_config(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"Config file {path} not found; skipping overrides.")
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
    if allow_float:
        return int(value)
    return value


def main() -> int:
    cfg = load_config(CFG_PATH)
    if cfg is None:
        return 0

    sources = cfg.get("sources") or []
    source = sources[0] if sources else None
    if source is None:
        print("No sources defined; nothing to override.")
    else:
        # ... (all source settings) ...
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
        
        # <<< DEBUGGING SECTION FOR CHANNEL/CHANNELFILE >>>
        
        raw_channel_file = os.getenv("TR_CHANNEL_FILE")
        raw_channels_hz = os.getenv("TR_CHANNELS_HZ")

        if raw_channel_file is not None and raw_channel_file.strip() != "":
            
            print("\n--- DEBUGGING CHANNEL FILE ---")
            
            # 1. Get CWD (where the script is running)
            cwd = os.getcwd()
            print(f"Python script Current Working Directory (CWD): {cwd}")

            # 2. Define file paths
            filename = raw_channel_file.strip()
            source_path = f"/data/{filename}" # Based on your repo root
            dest_path = os.path.join(cwd, filename) # CWD is /app

            print(f"Source file path: {source_path}")
            print(f"Destination file path (CWD): {dest_path}")

            # 3. Check if source exists
            source_exists = os.path.exists(source_path)
            print(f"Does source file exist at {source_path}? {source_exists}")
            
            if not source_exists:
                print(f"CRITICAL: Source file not found at {source_path}. Please ensure '{filename}' is in the ROOT of your project.")

            # 4. Set JSON config
            system["channelFile"] = filename
            system.pop('channels', None)
            print(f"Set JSON 'channelFile' to: {filename}")

            # 5. Attempt to copy the file
            print(f"Attempting to copy file from {source_path} to {dest_path}...")
            try:
                shutil.copy(source_path, dest_path)
                print("File copy SUCCEEDED.")
                print(f"Contents of CWD ({cwd}): {os.listdir(cwd)}")
            except Exception as e:
                print(f"CRITICAL: File copy FAILED. Error: {e}")

            print("--- END DEBUGGING ---")
            
        elif raw_channels_hz is not None and raw_channels_hz.strip() != "":
            # This logic remains the same
            
            # <<< THIS IS THE LINE THAT WAS FIXED (removed the period) >>>
            try:
                parts = [part.strip() for part in raw_channels_hz.split(",") if part.strip()]
                if not parts:
                    raise ValueError("no values supplied for TR_CHANNELS_HZ")
                system["channels"] = [int(float(part)) for part in parts]
                system.pop('channelFile', None)
                print(f"Using TR_CHANNELS_HZ. Removing 'channelFile' key.")
            except ValueError as exc:
                print(f"Skipping TR_CHANNELS_HZ: {exc}")
        # <<< END OF DEBUGGING SECTION >>>

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
