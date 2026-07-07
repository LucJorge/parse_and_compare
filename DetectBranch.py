import subprocess
import sys

# Detects the current Git branch name
def detect_branch() -> str:
	try:
		branch = subprocess.check_output(
			["git", "rev-parse", "--abbrev-ref", "HEAD"], # Sent this to the terminal to get the current branch name
			stderr=subprocess.DEVNULL,
			text=True,
		).strip()
	except (subprocess.CalledProcessError, FileNotFoundError): # if git is not installed or the command fails, return "No branch"
		return "No branch"

	return branch or "No branch" # if the branch name is empty, return "No branch"


if __name__ == "__main__":
	branch = detect_branch()
	print(branch)
	sys.exit(0 if branch != "No branch" else 1)
