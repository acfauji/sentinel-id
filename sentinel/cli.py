"""SENTINEL-ID CLI entrypoint."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sentinel.collectors.collect import run_collector
from sentinel.labeling import dedup, to_json
from sentinel.report.render import render_report, write_reports


def _text_from(source) -> str:
    """Read text from a file path (str/Path) or a file object."""
    if hasattr(source, "read"):
        return source.read()
    return Path(source).read_text(encoding="utf-8")


def cmd_collect(args: argparse.Namespace) -> None:
    evidence = run_collector(args.kind, args.value)
    deduped = dedup(evidence)
    text = to_json(deduped)
    if args.out:
        args.out.write(text)
        args.out.close()
    else:
        print(text)


def cmd_analyze(args: argparse.Namespace) -> None:
    from sentinel.analyze.ai import analyze
    text = _text_from(args.in_file)
    analysis = analyze(text, language=args.lang)
    if args.out:
        args.out.write(analysis)
        args.out.close()
    else:
        print(analysis)


def cmd_report(args: argparse.Namespace) -> None:
    from sentinel.labeling.evidence import Evidence
    text = _text_from(args.in_file)
    analysis = _text_from(args.analysis) if args.analysis else ""
    analysis_id = _text_from(args.analysis_id) if args.analysis_id else ""

    evidence_list = [Evidence(**{k: v for k, v in item.items() if k != "key"}) for item in json.loads(text)]
    reports = render_report(evidence_list, analysis, analysis_id, subject=args.subject)
    paths = write_reports(Path(args.out_dir), reports)
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
    p_report.add_argument(
        "--analysis-id", dest="analysis_id", type=argparse.FileType("r"), default=None
    )
    p_report.add_argument("--out-dir", dest="out_dir", type=str, default="out")
    p_report.add_argument("--subject", dest="subject", type=str, default="subject")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
