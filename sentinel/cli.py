"""SENTINEL-ID CLI entrypoint."""
from __future__ import annotations

import argparse
import sys
import json

from sentinel.collectors.collect import run_collector
from sentinel.labeling import dedup, to_json
from sentinel.report.render import render_report, write_reports


def cmd_collect(args: argparse.Namespace) -> None:
    evidence = run_collector(args.kind, args.value)
    deduped = dedup(evidence)
    text = to_json(deduped)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text)


def cmd_analyze(args: argparse.Namespace) -> None:
    from sentinel.analyze.ai import analyze
    text = args.in_file.read_text(encoding="utf-8")
    analysis = analyze(text, language=args.lang)
    if args.out:
        args.out.write_text(analysis, encoding="utf-8")
    else:
        print(analysis)


def cmd_report(args: argparse.Namespace) -> None:
    from sentinel.labeling.evidence import Evidence
    text = args.in_file.read_text(encoding="utf-8")
    analysis = args.analysis.read_text(encoding="utf-8") if args.analysis else ""
    analysis_id = args.analysis_id.read_text(encoding="utf-8") if args.analysis_id else ""

    evidence_list = [Evidence(**item) for item in json.loads(text)]
    reports = render_report(evidence_list, analysis, analysis_id, subject=args.subject)
    paths = write_reports(args.out_dir, reports)
    for p in paths:
        print(str(p))


def main() -> None:
    parser = argparse.ArgumentParser(prog="sentinel", description="SENTINEL-ID CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_collect = sub.add_parser("collect", help="Collect evidence for a value")
    p_collect.add_argument("kind", choices=["username", "email", "nik", "breach"])
    p_collect.add_argument("value")
    p_collect.add_argument("--out", type=argparse.FileType("w"), default=None)
    p_collect.set_defaults(func=cmd_collect)

    p_analyze = sub.add_parser("analyze", help="AI-analyze evidence JSON")
    p_analyze.add_argument("--in", dest="in_file", type=argparse.FileType("r"), default=sys.stdin)
    p_analyze.add_argument("lang", choices=["en", "id"], default="en")
    p_analyze.set_defaults(func=cmd_analyze)

    p_report = sub.add_parser("report", help="Render bilingual report")
    p_report.add_argument("--in", dest="in_file", type=argparse.FileType("r"), default=sys.stdin)
    p_report.add_argument("--analysis", dest="analysis", type=argparse.FileType("r"), default=None)
    p_report.add_argument("--analysis-id", dest="analysis_id", type=argparse.FileType("r"), default=None)
    p_report.add_argument("--out-dir", dest="out_dir", type=str, default="out")
    p_report.add_argument("--subject", dest="subject", type=str, default="subject")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
