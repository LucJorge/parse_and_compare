import subprocess
import sys
from pathlib import Path

# Detects the current Git branch name for a given project folder.
def detect_branch(project_path: str | Path | None = None) -> str:
    if project_path is None:
        return "No branch"

    project_path = Path(project_path).expanduser()
    if not project_path.exists() or not project_path.is_dir():
        return "No branch"

    command = ["git", "-C", str(project_path), "rev-parse", "--abbrev-ref", "HEAD"]

    try:
        branch = subprocess.check_output(
            command,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "No branch"

    return branch or "No branch"


if __name__ == "__main__":
    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    branch = detect_branch(project_path)
    print(branch)
    sys.exit(0 if branch != "No branch" else 1)
