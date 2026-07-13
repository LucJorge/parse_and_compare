import json
from pathlib import Path
from typing import Any

# Utility functions for building and saving reports, and formatting report text.
def build_report(
    branch: str,
    har_file: Path,
    entry_index: int,
    request_spec: dict[str, Any],
    expected_response: dict[str, Any],
    actual_response: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    result = "Ready for Testing" if comparison["ready_for_testing"] else "Code Review Needed"
    return {
        "branch": branch,
        "har_file": str(har_file.name),
        "entry_index": entry_index,
        "endpoint": request_spec["path"] + (f"?{request_spec['query']}" if request_spec["query"] else ""),
        "aspire_base_url": request_spec.get("aspire_base_url", ""),
        "expected_status": expected_response.get("status"),
        "actual_status": actual_response.get("status"),
        "header_diffs": comparison.get("header_diffs", []),
        "body_diff": comparison.get("body_diff", ""),
        "result": result,
    }


def save_report(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_name = f"report_{report['har_file'].replace('.har', '')}_{report['entry_index']:03d}.json"
    report_path = output_dir / report_name
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    return report_path


def format_report_text(report: dict[str, Any]) -> str:
    lines = [
        f"Branch: {report['branch']}",
        f"HAR file: {report['har_file']}",
        f"Entry index: {report['entry_index']}",
        f"Endpoint: {report['endpoint']}",
        f"Aspire base URL: {report['aspire_base_url']}",
        f"Expected status: {report['expected_status']}",
        f"Actual status: {report['actual_status']}",
        f"Result: {report['result']}",
    ]
    if report["header_diffs"]:
        lines.append("\nHeader differences:")
        lines.extend(report["header_diffs"])
    if report["body_diff"]:
        lines.append("\nBody diff:")
        lines.append(report["body_diff"])
    return "\n".join(lines)


def save_report_text(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / f"report_{report['har_file'].replace('.har', '')}_{report['entry_index']:03d}.txt"
    text_path.write_text(format_report_text(report), encoding="utf-8")
    return text_path
