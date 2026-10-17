"""Talk to a small Gemma model running locally via Ollama.

Everything here stays on your own laptop:
  - The only HTTP call goes to http://localhost:11434 (your Ollama server).
  - No cloud API is ever contacted, and no model is ever downloaded by
    this code. You pull the model yourself once with `ollama pull`.

If Ollama is not running (or the model is missing), analyze() returns a
clear error message instead of crashing, and the CLI falls back to the
rule-based report.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:1b"  # ~1 GB, runs on CPU — fine on an i5 / 8 GB laptop
DEFAULT_TIMEOUT = 120  # small local models can be slow on a first run


def build_prompt(findings):
    """Turn scraper findings into a short prompt for the local model.

    Keep it compact: small models have small context windows, and the
    prompt is the only thing the model sees — no raw HTML is sent.
    """
    missing_alt = ", ".join(
        img["src"] for img in findings["images_missing_alt"][:5]
    ) or "none"
    return (
        "You are a friendly WordPress consultant writing for a small-business "
        "owner who is not technical. Based on this one-page audit, list the "
        "TOP 5 fixes in priority order. For each fix give one plain-English "
        "sentence on what to do and one on why it matters. "
        "Keep the whole answer under 200 words. No markdown headings, "
        "just a numbered list.\n\n"
        f"Page title: {findings['title'] or '(missing)'} "
        f"({findings['title_length']} chars)\n"
        f"Meta description: {findings['meta_description'] or '(missing)'} "
        f"({findings['meta_description_length']} chars)\n"
        f"H1 count: {findings['heading_counts']['h1']}, "
        f"H2 count: {findings['heading_counts']['h2']}\n"
        f"Images: {findings['images_total']} total, "
        f"{len(findings['images_missing_alt'])} missing alt text "
        f"({missing_alt})\n"
        f"Links: {len(findings['links_internal'])} internal, "
        f"{len(findings['links_external'])} external\n"
        f"Mobile viewport tag: {'yes' if findings['viewport'] else 'no'}\n"
        f"Page size: {findings['page_size_kb']} KB, "
        f"fetch time: {findings['fetch_time_ms']} ms\n"
        f"WordPress signals: "
        f"{', '.join(findings['wordpress_signals']) or 'none detected'}\n"
    )


def analyze(findings, model=DEFAULT_MODEL, timeout=DEFAULT_TIMEOUT):
    """Ask the local Gemma model for prioritized fixes.

    Returns {"text": str | None, "error": str | None}.
    Exactly one of the two is set. `error` is a human-readable hint
    (Ollama down, model missing, timeout) — never a raw traceback.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": build_prompt(findings),
                "stream": False,
            },
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError:
        return {
            "text": None,
            "error": (
                "Could not reach Ollama at http://localhost:11434. "
                "Is Ollama running? Start it, then run: "
                f"ollama pull {model}"
            ),
        }
    except requests.exceptions.Timeout:
        return {
            "text": None,
            "error": (
                f"The local model took longer than {timeout} seconds. "
                "Try again, or re-run with --no-ai for the rule-based report."
            ),
        }

    if response.status_code == 404:
        return {
            "text": None,
            "error": (
                f"Model '{model}' not found in Ollama. "
                f"Pull it once with: ollama pull {model}"
            ),
        }
    if response.status_code != 200:
        return {
            "text": None,
            "error": f"Ollama returned HTTP {response.status_code}.",
        }

    return {"text": response.json().get("response", "").strip(), "error": None}
