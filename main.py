import json
import sys
from pathlib import Path
from DetectBranch import detect_branch

# Load the configuration from a JSON file to persist the project root directory.
def load_config(config_path: Path):
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}

# Save the configuration to a JSON file to persist the project root directory.
def save_config(config_path: Path, config):
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)

# Get the project root directory from the user or from the config file.
def get_project_root():
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / "config.json"
    config = load_config(config_path)

    if config.get("project_root"):
        return Path(config["project_root"]).expanduser().resolve()

    while True:
        answer = input("PLL Core Platform folder: ").strip().strip('"')
        if not answer:
            print("The folder cannot be empty.")
            continue
        project_root = Path(answer).expanduser()
        if not project_root.is_absolute():
            project_root = (Path.cwd() / project_root).resolve()
        if project_root.exists():
            config["project_root"] = str(project_root)
            save_config(config_path, config)
            return project_root
        print(f"Folder not found: {project_root}")


# Get the name of the HAR file from the user.
def get_har_file_name():
    while True:
        har_name = input("Name of the .har file in the hars folder: ").strip().strip('"')
        if not har_name:
            print("The file name cannot be empty.")
            continue
        return har_name


# Resolve the HAR file path based on the script directory and the provided HAR file name.
def resolve_har_path(script_dir: Path, har_name: str):
    input_dir = (script_dir / "hars").resolve()
    input_dir.mkdir(parents=True, exist_ok=True)

    candidate = Path(har_name).expanduser()
    if not candidate.is_absolute():
        candidate = (input_dir / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not str(candidate).startswith(str(input_dir)):
        print(f"The HAR file must be inside: {input_dir}")
        return None

    return candidate


# Start of the pipeline
def run_pipeline():
    # Get the project root and the HAR file path
    project_root = get_project_root()
    # Print the current Git branch of the selected PPL Core Platform project
    print(f"Branch of PPL Core Platform project: {detect_branch(project_root)}")

    # Get the script directory and the HAR file path
    script_dir = Path(__file__).resolve().parent
    har_name = get_har_file_name()
    har_path = resolve_har_path(script_dir, har_name)

    if har_path is None:
        sys.exit(2)

    print(f"Project found at: {project_root}")
    
    import GetEndpoint

    # Call the get_endpoints function from GetEndpoint.py to process the HAR file
    success = GetEndpoint.get_endpoints(str(har_path))
    if success:
        print("DONE: All endpoints extracted successfully.")
    else:
        sys.exit(2)


if __name__ == "__main__":
    run_pipeline()
