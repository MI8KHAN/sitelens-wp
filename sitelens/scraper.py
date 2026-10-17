"""Fetch a web page and extract the signals SiteLens audits.

Only requests + BeautifulSoup are used. The scraper makes exactly one
HTTP GET to the URL being audited and sends nothing anywhere else.

Two steps, kept separate so tests can run offline:
  1. fetch(url)  -> downloads the page, returns (html, info)
  2. parse(html, url, info) -> returns a dict of findings
"""

import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 15
USER_AGENT = "SiteLens-WP/0.1 (local audit tool)"


def fetch(url, timeout=DEFAULT_TIMEOUT):
    """Download one page.

    Returns (html_text, info) where info holds status code, fetch time
    and page size. Raises requests.RequestException on network failure
    and requests.HTTPError on a bad HTTP status.
    """
    started = time.time()
    response = requests.get(
        url, timeout=timeout, headers={"User-Agent": USER_AGENT}
    )
    elapsed_ms = int((time.time() - started) * 1000)
    info = {
        "status_code": response.status_code,
        "fetch_time_ms": elapsed_ms,
        "page_size_kb": round(len(response.content) / 1024, 1),
        "final_url": response.url,  # after any redirects
    }
    response.raise_for_status()
    return response.text, info


def _is_internal(link_url, base_netloc):
    """True if a link points to the same site (or is a relative link)."""
    netloc = urlparse(link_url).netloc
    return netloc == "" or netloc == base_netloc


def parse(html, url, info=None):
    """Extract audit findings from already-downloaded HTML.

    `info` is the dict returned by fetch(); pass None when parsing a
    local fixture in tests.
    """
    soup = BeautifulSoup(html, "html.parser")
    info = info or {}
    base_netloc = urlparse(url).netloc

    # --- Basic page info -------------------------------------------------
    title_tag = soup.title
    title = title_tag.get_text(strip=True) if title_tag else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = (desc_tag.get("content") or "").strip() if desc_tag else ""
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    viewport = (viewport_tag.get("content") or "").strip() if viewport_tag else ""
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href") if canonical_tag else ""
    html_tag = soup.find("html")
    language = html_tag.get("lang", "") if html_tag else ""

    # --- Headings ---------------------------------------------------------
    headings = []
    for level in ("h1", "h2", "h3", "h4", "h5", "h6"):
        for tag in soup.find_all(level):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})
    heading_counts = {
        level: sum(1 for h in headings if h["level"] == level)
        for level in ("h1", "h2", "h3", "h4", "h5", "h6")
    }

    # --- Images -----------------------------------------------------------
    images = soup.find_all("img")
    missing_alt = []
    for img in images:
        alt = img.get("alt")
        if alt is None or alt.strip() == "":
            missing_alt.append({"src": img.get("src", "")})

    # --- Links ------------------------------------------------------------
    internal_links, external_links = [], []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue  # anchors and non-web links are not audited
        absolute = urljoin(url, href)
        entry = {"href": absolute, "text": tag.get_text(strip=True)[:80]}
        if _is_internal(absolute, base_netloc):
            internal_links.append(entry)
        else:
            external_links.append(entry)

    # --- WordPress signals ------------------------------------------------
    # These are just hints ("looks like WordPress"), not a guarantee.
    wp_signals = []
    generator = soup.find("meta", attrs={"name": "generator"})
    if generator and "wordpress" in (generator.get("content") or "").lower():
        wp_signals.append("generator meta tag says WordPress")
    page_text = html.lower()
    if "wp-content" in page_text or "wp-includes" in page_text:
        wp_signals.append("wp-content / wp-includes paths found")

    # --- Rule-based checks -------------------------------------------------
    # status is "pass", "warn" or "fail". Keep the wording plain-English:
    # a freelancer hands this report to a non-technical client.
    checks = []
    if not title:
        checks.append(
            {"name": "Page title", "status": "fail",
             "detail": "No <title> tag found. Search results will show a plain URL."}
        )
    elif len(title) > 60:
        checks.append(
            {"name": "Page title", "status": "warn",
             "detail": f"Title is {len(title)} characters — Google usually shows ~60."}
        )
    else:
        checks.append(
            {"name": "Page title", "status": "pass",
             "detail": f"Title is {len(title)} characters."}
        )

    if not description:
        checks.append(
            {"name": "Meta description", "status": "warn",
             "detail": "No meta description. Search results will pick random page text."}
        )
    elif len(description) > 160:
        checks.append(
            {"name": "Meta description", "status": "warn",
             "detail": f"Description is {len(description)} characters — keep it under ~160."}
        )
    else:
        checks.append(
            {"name": "Meta description", "status": "pass",
             "detail": f"Description is {len(description)} characters."}
        )

    if heading_counts["h1"] == 0:
        checks.append(
            {"name": "Main heading (H1)", "status": "fail",
             "detail": "No H1 found. Every page needs exactly one main heading."}
        )
    elif heading_counts["h1"] > 1:
        checks.append(
            {"name": "Main heading (H1)", "status": "warn",
             "detail": f"Found {heading_counts['h1']} H1 tags — use exactly one."}
        )
    else:
        checks.append(
            {"name": "Main heading (H1)", "status": "pass",
             "detail": "Exactly one H1 found."}
        )

    if missing_alt:
        checks.append(
            {"name": "Image alt text", "status": "warn",
             "detail": f"{len(missing_alt)} of {len(images)} images have no alt text — "
                       "bad for accessibility and image search."}
        )
    else:
        checks.append(
            {"name": "Image alt text", "status": "pass",
             "detail": f"All {len(images)} images have alt text."}
        )

    if not viewport:
        checks.append(
            {"name": "Mobile viewport", "status": "fail",
             "detail": "No viewport meta tag — the page may not scale on phones."}
        )
    else:
        checks.append(
            {"name": "Mobile viewport", "status": "pass",
             "detail": "Viewport meta tag present."}
        )

    size_kb = info.get("page_size_kb")
    if size_kb is not None and size_kb > 1000:
        checks.append(
            {"name": "Page weight", "status": "warn",
             "detail": f"Page is {size_kb} KB — over ~1 MB usually means slow load."}
        )
    elif size_kb is not None:
        checks.append(
            {"name": "Page weight", "status": "pass",
             "detail": f"Page is {size_kb} KB."}
        )

    return {
        "url": url,
        "status_code": info.get("status_code"),
        "fetch_time_ms": info.get("fetch_time_ms"),
        "page_size_kb": size_kb,
        "title": title,
        "title_length": len(title),
        "meta_description": description,
        "meta_description_length": len(description),
        "headings": headings,
        "heading_counts": heading_counts,
        "images_total": len(images),
        "images_missing_alt": missing_alt,
        "links_internal": internal_links,
        "links_external": external_links,
        "viewport": viewport,
        "canonical": canonical,
        "language": language,
        "wordpress_signals": wp_signals,
        "checks": checks,
    }
