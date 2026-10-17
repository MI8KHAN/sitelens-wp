# SiteLens WP — get a real first-user quote TODAY (Sat Oct 17)

Why today: the DEV post needs a real first-user quote OR Section 5 must be
deleted. A quote needs another person + waiting time, so asking on Sunday
is too late. Deadline: Mon Oct 19, ~11:59 AM PKT (Oct 18, 11:59 PM PDT).

## Who to ask
One classmate or friend with a WordPress site. Text only — no call needed.
Your own test run on ayunfortinn.com does NOT count as a first user
(see dev-post-outline.md Section 5).

## Copy-paste ask (send after the repo is public)
> Salam — quick favour, 2 minutes? I built a small tool that audits a
> WordPress site and gives a plain-English report. Could you run it once
> on your site and tell me in 1–2 sentences what it found and what you
> thought? Repo: <paste your sitelens-wp repo URL>
> Commands: pip install -r requirements.txt
> python -m sitelens audit <your-site-URL> --no-ai
> No need to install anything else. Thanks!

Note: send the --no-ai version so they do NOT need Ollama / Gemma.
That keeps it a 2-minute favour.

## What to ask back
Ask them to reply with:
1. What site they audited
2. One thing the report found
3. One sentence on whether the report was easy to understand

## Using the quote (Sunday writing)
- Use their real words, 2–3 sentences max, with their first name only
  (ask "okay to quote you by first name in my DEV post?").
- Do NOT invent, polish into a fake testimonial, or present the Ayun
  audit as a first user.

## If nobody replies by Sun Oct 18, ~10:00 AM PKT
Delete the whole Section 5 (First User) from the post and submit without
it. The official template says to remove it if nobody has used the tool
yet — submitting without it is safe. Do NOT submit with the placeholder.

## Sunday writing — 6 sections, keep it in your own words
1. What I built (2–3 short paragraphs) — what it does, what it checks
2. The problem (1–2 paragraphs) — why small sites / freelancers need it
3. Who would pay (short list + one price, e.g. $25 per audit report)
4. Why open matters (the key paragraph) — privacy, $0 per-report cost,
   no vendor lock-in
5. First user (real quote OR delete whole section — see above)
6. How it's built (short) — Python, BeautifulSoup, Ollama + Gemma 3 1B
   locally, single HTML report. Repo link + 3 run commands.
Tags must be exactly: devchallenge, hf26challenge
Category: Best Use of Gemma — name Gemma explicitly.
Demo: paste the unlisted 60–90 sec video link, not screenshots alone.
