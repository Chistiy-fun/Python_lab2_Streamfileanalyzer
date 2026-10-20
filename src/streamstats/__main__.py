import argparse
import sys

from streamstats.analysis import Stats
from streamstats.parsers import parse_jsonl, parse_csv
from streamstats.report import build_report, write_json_report
from streamstats.errors import StreamStatsError

def main():
    parser = argparse.ArgumentParser(prog="streamstats")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Анализ файлов событий"
    )

    analyze_parser.add_argument("input", nargs="+", help="Path to the input JSONL file")
    analyze_parser.add_argument("--output", default=None, help="Path to the output JSONL file")
    analyze_parser.add_argument("--skip-invalid", action="store_true", help="Skip invalid events")
    analyze_parser.add_argument("--format", choices=["jsonl", "csv"], default="jsonl", help="Input file format (default: jsonl)")

    args = parser.parse_args()

    match args.format:
        case "jsonl":
            parse_file = parse_jsonl
        case "csv":
            parse_file = parse_csv

    stats = Stats()

    for input_file in args.input:
        for event in parse_file(input_file, skip_invalid=args.skip_invalid, on_invalid=stats.record_invalid):
            stats.add(event)

    report = build_report(stats)

    if args.output is not None:
        write_json_report(report, args.output)
    else:
        write_json_report(report, "report.json")



if __name__ == "__main__":
    try:
        main()
    except (StreamStatsError, OSError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        raise SystemExit(2)
