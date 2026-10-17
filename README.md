# SiteLens WP — local-AI WordPress site audit for freelancers

A small Python CLI that audits any WordPress site and produces a
plain-English, client-ready HTML report a freelancer can hand to a client.

Built for the Hacktoberfest Week 2 "Side Hustle" challenge: build something
with open-weight models / open-source AI that someone would actually pay for.

## How it works

1. **Scraper** — downloads one page and checks the basics: title, meta
   description, heading outline, images missing alt text, internal/external
   links, mobile viewport, page weight.
2. **Local AI (optional)** — a small Gemma model running on your own laptop
   via Ollama turns those signals into a prioritized, plain-English fix list.
3. **Report** — everything is rendered as one self-contained HTML file.

**Privacy promise: all data stays local.** The scraper makes one HTTP GET to
the page being audited. The AI step talks only to `http://localhost:11434`
(your own Ollama server). No client data is ever sent to a cloud API.

## One-time setup

```bash
# 1. Python 3.10+ (check with: python --version)
# 2. Install the only two dependencies:
pip install -r requirements.txt

# 3. Install Ollama from https://ollama.com (skip this if you only want
#    the rule-based report — see --no-ai below)
# 4. Pull a small Gemma model once (~1 GB download, runs on CPU):
ollama pull gemma3:1b
```

## Run an audit

```bash
# Full audit with AI findings (Ollama must be running):
python -m sitelens audit https://example.com

# Write the report somewhere specific:
python -m sitelens audit https://example.com --output my-report.html

# Rule-based checks only, no AI (works without Ollama):
python -m sitelens audit https://example.com --no-ai

# Use a different local model:
python -m sitelens audit https://example.com --model gemma3:1b
```

Open the generated `report.html` in any browser — or email it to a client.

## Run the offline smoke test

```bash
python tests/test_smoke.py
```

No internet needed: it audits a local HTML fixture and checks the report.

## Troubleshooting

- **"Could not reach Ollama"** — Ollama isn't running. Start the Ollama app
  (or run `ollama serve`), then try again. Or use `--no-ai`.
- **"Model 'gemma3:1b' not found"** — run `ollama pull gemma3:1b` once.
- **AI is slow** — normal on a first run while the model loads; later runs
  are faster. `--no-ai` is instant.
- **"Could not fetch the page"** — check the URL and your connection.
  The URL must start with `http://` or `https://`.

## Who would pay for this

Freelancers and small agencies selling "site audits" as a service — a
classic Fiverr / LinkedIn gig. The tool also works as a standalone product
on Gumroad: run audits for clients, or sell the tool itself.
