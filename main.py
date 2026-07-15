"""Entry point for the HAR replay pipeline.

Flow: pick a .har file -> extract its requests/expected responses via
GetEndpoint/har_extractor -> replay each request against the local backend
via request_runner -> compare the real response to the expected one via
response_comparator -> save the outcome via reporter.
"""

import sys
from pathlib import Path
from DetectBranch import detect_branch
from config import get_project_root, get_local_base_url
from har_extractor import load_har, choose_entry, extract_request, transform_to_local_url
from request_runner import send_request, wait_for_backend
from response_comparator import compare_response
from reporter import build_report, save_report, format_report_text
from GetEndpoint import get_endpoints, find_processed_entries, parse_http_file, resolve_processed_entries_dir


# Resolves a HAR file name to a path inside the hars/ folder, rejecting anything outside it.
def resolve_har_path(script_dir: Path, har_name: str) -> Path | None:
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

    if not candidate.is_file():
        print(f"HAR file not found: {candidate}")
        return None

    return candidate


# Runs a single processed .http entry end-to-end and returns its comparison result.
def run_entry(script_dir, branch, har_path, har, local_base_url, entry_index, http_file):
    # Rebuild the original request from the saved .http file and pair it with
    # the expected response recorded in the HAR for the same entry.
    parsed_request = parse_http_file(http_file)
    entry, _ = choose_entry(har, preferred_index=entry_index)
    expected_response = extract_request(entry)["expected_response"]

    target_url = transform_to_local_url(parsed_request["url"], local_base_url)
    request_spec = {
        "method": parsed_request["method"],
        "headers": parsed_request["headers"],
        "body": parsed_request["body"],
        "original_url": parsed_request["url"],
        "target_url": target_url,
    }

    print(f"[{entry_index}] {request_spec['method']} {target_url}")
    actual_response = send_request(request_spec, target_url)
    comparison = compare_response(expected_response, actual_response)

    # Persist a report for this entry so results can be reviewed later.
    report = build_report(
        branch=branch,
        har_file=har_path,
        entry_index=entry_index,
        request_spec=request_spec,
        expected_response=expected_response,
        actual_response=actual_response,
        comparison=comparison,
    )

    report_path = save_report(report, script_dir / "reports")
    print(format_report_text(report))
    print(f"Report saved to: {report_path}")
    print(f"[{entry_index}] {'Ready for Testing' if comparison['ready_for_testing'] else 'Code Review Needed'}")

    return comparison["ready_for_testing"]


# Main function to run the pipeline
def run_pipeline():
    script_dir = Path(__file__).resolve().parent
    project_root = get_project_root(script_dir)
    branch = detect_branch(project_root)
    print(f"Branch: {branch}")

    local_base_url = get_local_base_url(script_dir)

    # Ask for the HAR file to replay and make sure it lives in hars/.
    har_name = input("Name of the .har file in the hars folder: ").strip().strip('"')
    har_name = har_name + ".har" if not har_name.endswith(".har") else har_name
    har_path = resolve_har_path(script_dir, har_name)
    if har_path is None:
        sys.exit(2)

    # Extract every entry of the HAR into individual .http/.json files under processed_hars/.
    print(f"Processing {har_path.name}...")
    if not get_endpoints(har_path):
        print(f"Failed to process HAR file: {har_path}")
        sys.exit(2)

    processed_dir = resolve_processed_entries_dir(har_path)
    entries = find_processed_entries(processed_dir)
    if not entries:
        print(f"No processed entries found in: {processed_dir}")
        sys.exit(2)

    print(f"Waiting for backend at {local_base_url}...")
    if not wait_for_backend(local_base_url):
        print("Backend did not become available in time.")
        sys.exit(2)

    har = load_har(har_path)

    # Replay each extracted entry against the local backend and track overall success.
    all_ready = True
    for entry_index, http_file in entries:
        ready = run_entry(script_dir, branch, har_path, har, local_base_url, entry_index, http_file)
        all_ready = all_ready and ready

    return 0 if all_ready else 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
