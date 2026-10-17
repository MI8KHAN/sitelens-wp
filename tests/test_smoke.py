"""Offline smoke test: scraper + report against a local fixture.

No internet needed — the fixture is a file on disk, and the Gemma step
is never called here. Run from the project root:

    python tests/test_smoke.py

Also works under pytest (each test_* function runs standalone).
"""

import pathlib
import sys

# Make `import sitelens` work no matter where the test is run from.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sitelens.scraper import parse  # noqa: E402
from sitelens.report import render_html  # noqa: E402

FIXTURE = pathlib.Path(__file__).resolve().parent / "fixtures" / "sample-page.html"
URL = "https://acme-bakery.example/"


def load_findings():
    html = FIXTURE.read_text(encoding="utf-8")
    fake_info = {"status_code": 200, "fetch_time_ms": 12, "page_size_kb": 1.8}
    return parse(html, URL, fake_info)


def test_title_and_wordpress_signals():
    findings = load_findings()
    assert findings["title"].startswith("Acme Bakery")
    assert "generator meta tag says WordPress" in findings["wordpress_signals"]
    assert "wp-content / wp-includes paths found" in findings["wordpress_signals"]


def test_missing_meta_description_is_flagged():
    findings = load_findings()
    assert findings["meta_description"] == ""
    check = next(c for c in findings["checks"] if c["name"] == "Meta description")
    assert check["status"] == "warn"


def test_two_h1s_are_flagged():
    findings = load_findings()
    assert findings["heading_counts"]["h1"] == 2
    check = next(c for c in findings["checks"] if c["name"] == "Main heading (H1)")
    assert check["status"] == "warn"


def test_missing_alt_and_viewport():
    findings = load_findings()
    assert findings["images_total"] == 3
    assert len(findings["images_missing_alt"]) == 1
    assert findings["images_missing_alt"][0]["src"].endswith("cake.jpg")
    check = next(c for c in findings["checks"] if c["name"] == "Mobile viewport")
    assert check["status"] == "fail"


def test_links_classified():
    findings = load_findings()
    internal = {link["href"] for link in findings["links_internal"]}
    external = {link["href"] for link in findings["links_external"]}
    assert "https://acme-bakery.example/menu" in internal
    assert "https://instagram.com/acmebakery" in external


def test_report_renders():
    findings = load_findings()
    report = render_html(
        findings, ai_text="1. Add a meta description.", ai_error=None
    )
    assert "Acme Bakery" in report
    assert "AI recommendations" in report
    assert "<script>" not in report  # nothing unescaped sneaks in


def main():
    """Run every test_* function and report the result."""
    tests = [
        (name, fn)
        for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
        else:
            print(f"PASS {name}")
    print(f"{len(tests) - failed}/{len(tests)} smoke tests passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
