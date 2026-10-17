# DEV submission post outline — SiteLens WP
<!-- Follow the official Hacktoberfest Week 2 "Side Hustle" Submission Template.
     Judging weights WRITING quality most — write this in your own words,
     with your own story. This outline is scaffolding, not the post itself. -->

## Title (pick one, make it yours)
- SiteLens WP: A Local-AI WordPress Audit Tool Freelancers Can Actually Sell
- I Built a WordPress Audit Tool That Runs Entirely on My Laptop

## 1. What I built (2–3 paragraphs)
- SiteLens WP: a small Python CLI. Give it a WordPress URL, get a
  plain-English, client-ready HTML audit report.
- What it checks: title, meta description, heading outline, images missing
  alt text, internal/external links, mobile viewport, page weight.
- The AI step: a small Gemma model running locally via Ollama turns the raw
  signals into a prioritized fix list — no cloud API involved.
- Demo: the official template asks for a deployed link OR a video demo — screenshots alone do not satisfy it. SiteLens is a local CLI, so record a short (60–90 sec) screen recording: run the audit on a real site, open the HTML report, show the verdict + checks table. Upload it (unlisted YouTube / Loom / direct link) and put the link in the Demo section. Screenshots help, but the video/link is the required part.

## 2. The problem (1–2 paragraphs)
- Small businesses know their site "isn't working" but can't read
  technical SEO reports. Freelancers re-check the same basics by hand on
  every client site — slow, repetitive, easy to miss things.
- Existing audit tools either cost per-report API fees or send client data
  to a third party. Neither fits a $25 audit gig.

## 3. Who would pay for it (1 paragraph + short list)
- Freelancers and small agencies selling site audits as a service
  (Fiverr / LinkedIn gig). They charge for the report; the tool costs
  them $0 per report.
- Small-business owners who want a readable audit of their own site.
- Later: sell the tool itself on Gumroad.
- Be concrete: what would you charge? (e.g. "$25 per audit report.")

## 4. Why open innovation matters (the key paragraph — do not skip)
- **Privacy:** client site data never leaves the freelancer's laptop — no
  sending client assets to a third-party API.
- **Cost:** zero per-report API fees. A $5/report API cost kills a $25 gig;
  local inference is free, so the margins make a side hustle actually work.
- **Independence:** no vendor lock-in, no surprise price changes breaking
  the product later.

## 5. First-user story (placeholder — fill in with a real one OR DELETE THIS WHOLE SECTION)
**⚠️ Do NOT submit with this placeholder in it.** The official template says to remove the First User section if nobody has used the tool yet. The Ayun audit does NOT count — that was your own test run, not someone else using the tool. Either (a) get one real person (classmate / friend) to run SiteLens on their site today and quote them, or (b) delete this entire Section 5 before submitting.
- [ ] Audit one real person's WordPress site (classmate / friend / your own)
  for free.
- [ ] Write 2–3 sentences: who they are, what the audit found, what they
  said about it. A real quote beats any feature list.

## 6. How it's built (short tech section)
- Python, requests + BeautifulSoup for the scraper; Ollama + Gemma 3 1B
  (quantized, ~1 GB) running locally on CPU; single self-contained HTML
  report. Repo link + how to run: `pip install -r requirements.txt`,
  `ollama pull gemma3:1b`, `python -m sitelens audit <url>`.

## Submission checklist (before Oct 18, 11:59 PM PDT / Oct 19 ~11:59 AM PKT)
- [ ] DEV post uses the official Side Hustle Submission Template.
- [ ] Post tags are exactly `devchallenge, hf26challenge` (from the official prefill link).
- [ ] GitHub repo exists and is public: create a repo, push the scaffold, and check the link opens while logged out. The Code section embeds this repo.
- [ ] Repo link works; README setup steps tested on a clean machine.
- [ ] Demo is a video demo link (or deployed link), not screenshots alone — 60–90 sec screen recording of a real audit + the HTML report. Screenshots are extra, not a substitute.
- [ ] First-user story filled in with a real quote — or delete the My First User section if no one has used it yet (template says to remove it if not).
- [ ] Category: Best Use of Gemma (primary). Mention Gemma explicitly.
- [ ] Read the official rules once more for eligibility fine print.
