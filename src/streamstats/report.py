from streamstats.analysis import Stats
import json
import csv

def build_report(stats: Stats) -> dict:
    return {
        "total_records": stats.total_events + stats.skipped_invalid,
        "total_events": stats.total_events,
        "skipped_invalid": stats.skipped_invalid,
        "counts_by_level": dict(stats.counts_by_level),
        "counts_by_source": dict(stats.counts_by_source),
        "error_counts_by_source": dict(stats.error_counts_by_source),
        "first_timestamp": stats.first_timestamp.isoformat() if stats.first_timestamp else None,
        "last_timestamp": stats.last_timestamp.isoformat() if stats.last_timestamp else None,
        "top_error_sources": stats.top_error_sources(),
    }


def write_json_report(report: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def write_csv_report(report: dict, path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "key", "value"])

        for key in ["total_records", "total_events", "skipped_invalid"]:
            writer.writerow(["summary", key, report[key]])

        for section in ("counts_by_level", "counts_by_source", "error_counts_by_source"):
            for key, value in report[section].items():
                writer.writerow([section, key, value])

        for key in ["first_timestamp", "last_timestamp"]:
            writer.writerow(["timestamps", key, report[key]])

        for source, count in report["top_error_sources"]:
            writer.writerow(["top_error_sources", source, count])
