"""Loads and persists user-specific settings (project root, local backend URL) in config.json.

Settings are asked for interactively once and then cached, so subsequent runs
of main.py don't prompt again.
"""

import json
from pathlib import Path

DEFAULT_LOCAL_BASE_URL = "https://localhost:7078/api/Core"


def load_config(config_path: Path) -> dict:
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def save_config(config_path: Path, config: dict) -> None:
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)


# Returns the PPL Core Platform folder, asking the user for it (and caching the answer) on first use.
def get_project_root(script_dir: Path) -> Path:
    config_path = script_dir / "config.json"
    config = load_config(config_path)
    project_root = config.get("project_root")

    if project_root:
        return Path(project_root).expanduser().resolve()

    while True:
        answer = input("PPL Core Platform folder: ").strip().strip('"')
        if not answer:
            print("The folder cannot be empty.")
            continue

        resolved = Path(answer).expanduser()
        if not resolved.is_absolute():
            resolved = (Path.cwd() / resolved).resolve()

        if resolved.exists():
            config["project_root"] = str(resolved)
            save_config(config_path, config)
            return resolved

        print(f"Folder not found: {resolved}")


# Returns the local backend base URL (e.g. https://localhost:7078/api/Core), persisting it on first use.
def get_local_base_url(script_dir: Path) -> str:
    config_path = script_dir / "config.json"
    config = load_config(config_path)
    local_base_url = config.get("local_base_url")

    if local_base_url:
        return local_base_url.rstrip("/")

    answer = input(f"Local backend base URL [default: {DEFAULT_LOCAL_BASE_URL}]: ").strip()
    local_base_url = (answer or DEFAULT_LOCAL_BASE_URL).rstrip("/")
    config["local_base_url"] = local_base_url
    save_config(config_path, config)
    return local_base_url
