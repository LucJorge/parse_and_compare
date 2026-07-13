import json
from pathlib import Path

# Utility functions for loading and saving configuration, and determining the project root directory.
def load_config(config_path: Path) -> dict:
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def save_config(config_path: Path, config: dict) -> None:
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)


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
