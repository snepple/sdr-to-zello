#!/usr/bin/env python3
import json
import os
import sys
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
        return float(value) # FIXED: Return float if float is allowed
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
        set_env(cfg, "TR_CENTER_HZ", lambda raw: source.__setitem__("center", coerce_int(raw, "center", allow_float=True)))
        set_env(cfg, "TR_SAMPLE_RATE", lambda raw: source.__setitem__("rate", coerce_int(raw, "rate", allow_float=True)))
        set_env(cfg, "TR_ERROR_HZ", lambda raw: source.__setitem__("error", coerce_int(raw, "error", allow_float=True)))
        set_env(cfg, "TR_GAIN_DB", lambda raw: source.__setitem__("gain", coerce_int(raw, "gain", allow_float=True)))
        
    systems = cfg.get("systems") or []
    system = systems[0] if systems else None
    if system is None:
        print("No systems defined; skipping system overrides.")
    else:
        set_env(cfg, "TR_SQUELCH_DB", lambda raw: system.__setitem__("squelch", int(float(raw))))
        
        def set_channels(raw: str) -> None:
            parts = [part.strip() for part in raw.split(",") if part.strip()]
            if not parts:
                raise ValueError("no values supplied")
            system["channels"] = [int(float(part)) for part in parts]
            # Remove conflicting file setting
            system.pop("channelFile", None) 
        set_env(cfg, "TR_CHANNELS_HZ", set_channels)

        # --- BUG FIXES BELOW ---
        # Fixed capitalization from "AnalogLevels" to "analogLevels"
        set_env(
            cfg,
            "TR_ANALOG_LEVELS",
            lambda raw: system.__setitem__("analogLevels", coerce_int(raw, "analogLevels", allow_float=True)),
        )
        # Fixed capitalization from "DigitalLevels" to "digitalLevels"
        set_env(
            cfg,
            "TR_DIGITAL_LEVELS",
            lambda raw: system.__setitem__("digitalLevels", coerce_int(raw, "digitalLevels", allow_float=True)),
        )
        # -----------------------

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

    plugins = cfg.get("plugins") or []
    if plugins:
        plugin = plugins[0]
        streams = plugin.get("streams") or []
        stream = streams[0] if streams else None
        if stream:
            set_env(cfg, "TR_PLUGIN_PORT", lambda raw: stream.__setitem__("port", coerce_int(raw, "port")))
            set_env(cfg, "TR_PLUGIN_ADDRESS", lambda raw: stream.__setitem__("address", raw.strip()))
            set_env(cfg, "TR_PLUGIN_TGID", lambda raw: stream.__setitem__("TGID", int(raw, 0)))
            set_env(cfg, "TR_PLUGIN_SEND_JSON", lambda raw: stream.__setitem__("sendJSON", raw.strip().lower() in {"1", "true", "yes"}))
    else:
        print("No plugins configured; skipping plugin overrides.")

    write_config(CFG_PATH, cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
