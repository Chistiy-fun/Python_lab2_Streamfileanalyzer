import argparse
import sys

from streamstats.analysis import Stats
from streamstats.parsers import parse_jsonl, parse_csv
from streamstats.report import build_report, write_json_report, write_csv_report
from streamstats.errors import StreamStatsError
from streamstats.registry import PARSERS, get_parser, register_parser


register_parser("jsonl", parse_jsonl)
register_parser("csv", parse_csv)


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
    analyze_parser.add_argument("--format", choices=tuple(PARSERS), default="jsonl", help="Input file format (default: jsonl)")
    analyze_parser.add_argument("--report-format", choices=["json", "csv"], default="json", help="Output report format (default: json)")

    args = parser.parse_args()

    parse_file = get_parser(args.format)

    stats = Stats()

    for input_file in args.input:
        for event in parse_file(input_file, skip_invalid=args.skip_invalid, on_invalid=stats.record_invalid):
            stats.add(event)

    report = build_report(stats)

    match args.report_format:
        case "json":
            output_path = args.output if args.output is not None else "report.json"
            write_json_report(report, output_path)
        case "csv":
            output_path = args.output if args.output is not None else "report.csv"
            write_csv_report(report, output_path)
        case _:
            raise StreamStatsError(f"Unsupported report format: {args.report_format}")



if __name__ == "__main__":
    try:
        main()
    except (StreamStatsError, OSError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        raise SystemExit(2)
