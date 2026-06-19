# DLF NTH Kakkanad Ad Watcher

Monitors property sites for new listings of **DLF New Town Heights (NTH),
Kakkanad** and sends you a **WhatsApp message** (via Twilio) for each new ad.
Runs free on **GitHub Actions** every 30 minutes — no machine of your own needed.

Inspired by [bushyBee/OLXLookUp](https://github.com/bushyBee/OLXLookUp).

## Sites covered

| Site | Method | Reliability |
|------|--------|-------------|
| OLX | JSON search API | ✅ Primary, reliable |
| Housing.com | HTML scrape | ⚠️ Best-effort |
| 99acres | HTML scrape | ⚠️ Best-effort |
| MagicBricks | HTML scrape | ⚠️ Best-effort |

> Facebook Marketplace is intentionally excluded — it requires login and
> aggressively blocks automation, so it can't run unattended reliably.
>
> The "best-effort" sites may intermittently return nothing when they block
> static requests or change their markup. OLX is the dependable source; the
> rest are bonus coverage. To make them reliable, set a `SCRAPER_API_KEY`
> (ScrapingAnt — free tier at <https://scrapingant.com>): when present, the
> HTML scrapers route through it so JS-rendered, bot-protected pages load.
> Without a key they fall back to direct requests (which these sites often
> block). Add the key as a GitHub secret named `SCRAPER_API_KEY`.

## How it works

1. Each site scraper returns normalized `Ad` objects.
2. Ads are filtered to those mentioning **NTH / New Town Heights** *and*
   **Kakkanad** (see `config.py`).
3. New ads (not in `data/seen_ids.json`) trigger a WhatsApp message.
4. The updated seen list is committed back to the repo by the workflow, so you
   never get notified about the same ad twice.

## Setup

### 1. Twilio WhatsApp sandbox
1. Create a free account at <https://www.twilio.com>.
2. Open **Messaging → Try it out → Send a WhatsApp message**.
3. From your phone, send the sandbox join code (e.g. `join <word-word>`) to the
   Twilio sandbox number to opt in.
4. Note your **Account SID**, **Auth Token**, and the sandbox **From** number
   (`whatsapp:+14155238886`).

### 2. Run locally (test)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your Twilio values
python main.py --dry-run   # prints matches, sends nothing
```

Other modes:
```bash
python main.py --seed   # mark all current listings as seen (no messages)
python main.py          # real run: send WhatsApp for new ads + save state
```

### 3. Deploy on GitHub Actions (recommended)
1. Push this folder to a GitHub repo.
2. In **Settings → Secrets and variables → Actions**, add:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_FROM` (e.g. `whatsapp:+14155238886`)
   - `CONTACT_NUMBER` (e.g. `whatsapp:+9198XXXXXXXX`)
3. Go to the **Actions** tab and enable workflows.
4. First, run **Watch DLF NTH Kakkanad → Run workflow** once. On the very first
   run consider seeding so you don't get a burst of existing listings: run
   `python main.py --seed` locally and commit `data/seen_ids.json`, or just let
   the first scheduled run notify you of whatever is currently listed.
5. After that it runs automatically every 30 minutes.

## Tuning

- **What counts as a match** — edit `PROJECT_TERMS` / `LOCALITY_TERMS` in
  `config.py`.
- **Check frequency** — edit the `cron` in
  `.github/workflows/watch.yml` (GitHub's minimum is ~5 min, 30 min is gentle).
- **Add/remove a site** — add a module under `scrapers/` exposing
  `fetch() -> list[Ad]` and register it in `scrapers/__init__.py`.

## Notes / caveats

- Scraping these sites is generally against their Terms of Service and is fine
  for personal, low-volume use only. Expect occasional breakage when sites
  change their HTML or tighten bot protection.
- The "best-effort" scrapers use search URLs that may need updating over time.
