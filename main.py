import sys
from pathlib import Path
from DetectBranch import detect_branch
from config import get_project_root
from har_extractor import load_har, choose_entry, extract_request
from request_runner import send_request, wait_for_backend
from response_comparator import compare_response
from reporter import build_report, save_report, format_report_text
from GetEndpoint import get_endpoints

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

# Main function to run the pipeline
def run_pipeline():
    script_dir = Path(__file__).resolve().parent
    project_root = get_project_root(script_dir)
    print(f"Branch: {detect_branch(project_root)}")

    print("Processing HAR files in hars/...")
    get_endpoints(script_dir / "hars")

    har_name = input("Name of the .har file in the hars folder: ").strip().strip('"')
    har_path = resolve_har_path(script_dir, har_name)
    if har_path is None:
        sys.exit(2)

    har = load_har(har_path)
    entry, entry_index = choose_entry(har)
    extracted = extract_request(entry)
    request_spec = extracted["request"]
    expected_response = extracted["expected_response"]

    aspire_base_url = input("Aspire local base URL (e.g. http://localhost:5046): ").strip()
    request_spec["aspire_base_url"] = aspire_base_url

    print(f"Waiting for backend at {aspire_base_url}...")
    if not wait_for_backend(aspire_base_url):
        print("Backend did not become available in time.")
        sys.exit(2)

    # Send the request and compare the response
    actual_response = send_request(request_spec, aspire_base_url)
    comparison = compare_response(expected_response, actual_response)

    report = build_report(
        branch=detect_branch(project_root),
        har_file=har_path,
        entry_index=entry_index,
        request_spec=request_spec,
        expected_response=expected_response,
        actual_response=actual_response,
        comparison=comparison,
    )

    report_dir = script_dir / "reports"
    report_path = save_report(report, report_dir)
    print(format_report_text(report))
    print(f"Report saved to: {report_path}")

    if comparison["ready_for_testing"]:
        print("Ready for Testing")
        return 0

    print("Code Review Needed")
    return 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
