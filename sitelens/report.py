"""Render audit findings as a clean, client-ready HTML report.

The report is one self-contained HTML file (inline CSS, no external
assets), so a freelancer can email it straight to a client. All dynamic
text is HTML-escaped — a site's title or headings must never be able to
inject markup into the report.
"""

import html


def _esc(value):
    """HTML-escape anything that came from the audited page."""
    return html.escape(str(value if value is not None else ""))


def _badge(status):
    """Small coloured label for a check: pass / warn / fail."""
    return f'<span class="badge {status}">{status.upper()}</span>'


def render_html(findings, ai_text=None, ai_error=None):
    """Build the full HTML report string.

    findings: dict from scraper.parse()
    ai_text:  prioritized fixes from the local Gemma model (optional)
    ai_error: why AI findings are missing, if they are (optional)
    """
    title = findings["title"] or "(no title)"
    url = findings["url"]

    # --- Summary numbers --------------------------------------------------
    n_fail = sum(1 for c in findings["checks"] if c["status"] == "fail")
    n_warn = sum(1 for c in findings["checks"] if c["status"] == "warn")
    n_pass = sum(1 for c in findings["checks"] if c["status"] == "pass")
    if n_fail:
        verdict = f"Needs attention — {n_fail} issue(s) to fix"
        verdict_class = "fail"
    elif n_warn:
        verdict = f"Good start — {n_warn} improvement(s) suggested"
        verdict_class = "warn"
    else:
        verdict = "Looking good — no issues found"
        verdict_class = "pass"

    # --- Checks table -----------------------------------------------------
    check_rows = "".join(
        f"<tr><td>{_badge(c['status'])}</td>"
        f"<td><strong>{_esc(c['name'])}</strong></td>"
        f"<td>{_esc(c['detail'])}</td></tr>"
        for c in findings["checks"]
    )

    # --- Headings outline -------------------------------------------------
    if findings["headings"]:
        heading_rows = "".join(
            f"<tr><td>{_esc(h['level'])}</td><td>{_esc(h['text'])}</td></tr>"
            for h in findings["headings"]
        )
    else:
        heading_rows = "<tr><td colspan='2'>No headings found on this page.</td></tr>"

    # --- Images missing alt text ------------------------------------------
    if findings["images_missing_alt"]:
        alt_rows = "".join(
            f"<tr><td>{_esc(img['src'] or '(no src)')}</td></tr>"
            for img in findings["images_missing_alt"]
        )
    else:
        alt_rows = "<tr><td>All images have alt text.</td></tr>"

    # --- AI section ---------------------------------------------------------
    if ai_text:
        ai_section = (
            "<h2>AI recommendations (local Gemma model)</h2>"
            f"<p class='ai-note'>Generated on your laptop by a local Gemma "
            f"model — no page data left this computer.</p>"
            f"<div class='ai-box'>{_esc(ai_text)}</div>"
        )
    elif ai_error:
        ai_section = (
            "<h2>AI recommendations</h2>"
            f"<p class='ai-note'>Skipped: {_esc(ai_error)}</p>"
            "<p>Re-run without --no-ai once Ollama is running to add them.</p>"
        )
    else:
        ai_section = (
            "<h2>AI recommendations</h2>"
            "<p class='ai-note'>Skipped (ran with --no-ai).</p>"
        )

    wp_note = (
        "WordPress signals detected: "
        + _esc(", ".join(findings["wordpress_signals"]))
        if findings["wordpress_signals"]
        else "No clear WordPress signals detected on this page."
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site audit — {_esc(url)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 760px;
         margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; line-height: 1.5; }}
  h1 {{ font-size: 1.6rem; }} h2 {{ margin-top: 2rem; font-size: 1.2rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: .5rem; }}
  td, th {{ border: 1px solid #ddd; padding: .5rem; text-align: left;
            vertical-align: top; }}
  th {{ background: #f4f4f4; }}
  .verdict {{ font-size: 1.1rem; font-weight: bold; padding: .75rem;
             border-radius: 6px; }}
  .verdict.pass {{ background: #e6f6e6; }} .verdict.warn {{ background: #fff6d8; }}
  .verdict.fail {{ background: #ffe6e6; }}
  .badge {{ font-size: .75rem; font-weight: bold; padding: 2px 6px;
           border-radius: 4px; color: #fff; }}
  .badge.pass {{ background: #2e9e4f; }} .badge.warn {{ background: #d99a00; }}
  .badge.fail {{ background: #c0392b; }}
  .ai-box {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem;
            border-radius: 6px; }}
  .ai-note {{ color: #555; font-size: .9rem; }}
  footer {{ margin-top: 2.5rem; color: #777; font-size: .85rem; }}
</style>
</head>
<body>
<h1>Site audit</h1>
<p>Audited page: <a href="{_esc(url)}">{_esc(url)}</a></p>
<p class="verdict {verdict_class}">{_esc(verdict)}</p>

<h2>At a glance</h2>
<table>
  <tr><th>Page title</th><td>{_esc(title)} ({findings['title_length']} characters)</td></tr>
  <tr><th>Meta description</th><td>{_esc(findings['meta_description'] or '— none —')}
      ({findings['meta_description_length']} characters)</td></tr>
  <tr><th>Status / size / speed</th><td>HTTP {findings['status_code']} ·
      {findings['page_size_kb']} KB · {findings['fetch_time_ms']} ms to fetch</td></tr>
  <tr><th>Links</th><td>{len(findings['links_internal'])} internal ·
      {len(findings['links_external'])} external</td></tr>
  <tr><th>Images</th><td>{findings['images_total']} total ·
      {len(findings['images_missing_alt'])} missing alt text</td></tr>
  <tr><th>Platform</th><td>{wp_note}</td></tr>
</table>

<h2>Checks</h2>
<table>
  <tr><th>Status</th><th>Check</th><th>Detail</th></tr>
  {check_rows}
</table>

<h2>Heading outline</h2>
<table>
  <tr><th>Level</th><th>Text</th></tr>
  {heading_rows}
</table>

<h2>Images missing alt text</h2>
<table>
  <tr><th>Image source</th></tr>
  {alt_rows}
</table>

{ai_section}

<footer>Generated locally by SiteLens WP — no page data left this computer.</footer>
</body>
</html>
"""
