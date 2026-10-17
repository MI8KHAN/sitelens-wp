"""SiteLens WP command line.

Usage:
    python -m sitelens audit https://example.com
    python -m sitelens audit https://example.com --output my-report.html
    python -m sitelens audit https://example.com --no-ai

The audit always runs the rule-based checks. AI findings are added when
Ollama is running locally; --no-ai skips the model entirely (useful when
Ollama is not installed yet, or for a fast check).
"""

import argparse
import sys

from . import __version__, gemma
from .scraper import fetch, parse
from .report import render_html


def build_parser():
    parser = argparse.ArgumentParser(
        prog="sitelens",
        description="Audit a WordPress site and write a client-ready HTML report.",
    )
    parser.add_argument("--version", action="version", version=f"sitelens {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit one page of a site.")
    audit.add_argument("url", help="Full page URL, e.g. https://example.com")
    audit.add_argument(
        "--output", default="report.html",
        help="Where to write the HTML report (default: report.html).",
    )
    audit.add_argument(
        "--no-ai", action="store_true",
        help="Skip the local Gemma model; rule-based checks only.",
    )
    audit.add_argument(
        "--model", default=gemma.DEFAULT_MODEL,
        help=f"Ollama model to use (default: {gemma.DEFAULT_MODEL}).",
    )
    audit.add_argument(
        "--timeout", type=int, default=15,
        help="Seconds to wait for the page download (default: 15).",
    )
    return parser


def cmd_audit(args):
    """Run one audit end to end: fetch -> parse -> (AI) -> report file."""
    url = args.url
    if not url.startswith(("http://", "https://")):
        print("URL must start with http:// or https://", file=sys.stderr)
        return 2

    print(f"Fetching {url} ...")
    try:
        html_text, info = fetch(url, timeout=args.timeout)
    except Exception as exc:  # network / HTTP errors, shown plainly
        print(f"Could not fetch the page: {exc}", file=sys.stderr)
        return 1
    print(f"Got HTTP {info['status_code']} in {info['fetch_time_ms']} ms "
          f"({info['page_size_kb']} KB).")

    findings = parse(html_text, url, info)
    print(f"Checks: {len(findings['checks'])} rules evaluated.")

    ai_text = None
    if args.no_ai:
        print("Skipping AI findings (--no-ai).")
    else:
        print(f"Asking local model '{args.model}' for prioritized fixes ...")
        result = gemma.analyze(findings, model=args.model)
        if result["error"]:
            # Not fatal: the report still goes out with rule-based checks.
            print(f"AI findings skipped: {result['error']}")
            ai_text = None
            ai_error = result["error"]
        else:
            ai_text = result["text"]
            ai_error = None
            print("AI findings received.")
    if args.no_ai:
        ai_error = None  # report() shows the "--no-ai" note in this case

    report_html = render_html(findings, ai_text=ai_text, ai_error=ai_error)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(report_html)
    print(f"Report written to {args.output}")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "audit":
        return cmd_audit(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
