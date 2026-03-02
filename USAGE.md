# WhatsMyName CLI — Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Commands Reference](#commands-reference)
4. [Filtering](#filtering)
5. [Output & Export](#output--export)
6. [Connection Options](#connection-options)
7. [Data Management](#data-management)
8. [Categories](#categories)
9. [Deception-Focused Investigations](#deception-focused-investigations)
10. [Advanced Usage](#advanced-usage)
11. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from source (recommended)

```bash
git clone https://github.com/WebBreacher/WhatsMyName.git
cd WhatsMyName
pip install -e .
```

This installs the `wmn` command globally. You can run it from anywhere.

### Verify installation

```bash
wmn --version
# wmn 2.0.0
```

### First run — fetch all data sources

After installation, run the update command to fetch the full site database:

```bash
wmn --update
```

This downloads and caches site data from Sherlock (~478 sites) and Maigret (~3,013 sites), combining them with the built-in WhatsMyName (731) and extended (1,076) databases. After deduplication, you'll have **4,387+ unique sites**.

---

## Quick Start

### Basic username scan

```bash
wmn johndoe
```

This checks the username `johndoe` across all non-NSFW sites and displays results in real-time with a progress bar.

### Include NSFW sites

```bash
wmn johndoe --nsfw
```

### Scan specific categories

```bash
wmn johndoe --category dating,finance
```

### Export results to JSON

```bash
wmn johndoe --output json
```

### Fast scan with more workers

```bash
wmn johndoe --workers 200 --timeout 10
```

---

## Commands Reference

### Syntax

```
wmn [username] [options]
```

### Positional argument

| Argument   | Description                        |
|------------|------------------------------------|
| `username` | The username to search for. Required for scanning, optional for data management commands. |

### Output options

| Flag                     | Description                                           |
|--------------------------|-------------------------------------------------------|
| `-o, --output FORMAT`    | Export results. FORMAT: `json`, `csv`, or `html`      |
| `--output-file PATH`    | Custom output file path (overrides `<username>.<ext>`) |
| `--found-only`           | Only display/export sites where the username was found |
| `-v, --verbose`          | Show errors, timeouts, and debug info during scan     |
| `--no-color`             | Disable colored terminal output                       |
| `--no-banner`            | Skip the ASCII banner                                 |

### Filtering

| Flag                          | Description                                    |
|-------------------------------|------------------------------------------------|
| `-c, --category CAT`         | Comma-separated categories to include          |
| `--exclude-category CAT`     | Comma-separated categories to exclude          |
| `--nsfw`                      | Include NSFW sites (excluded by default)       |
| `--site NAME`                | Check specific site(s) only. Repeatable.       |

### Connection

| Flag                | Description                                              |
|---------------------|----------------------------------------------------------|
| `-t, --timeout SEC` | Per-request timeout in seconds (default: 15)             |
| `-w, --workers N`   | Max concurrent HTTP requests (default: 100)              |
| `--proxy URL`       | Route through proxy (e.g. `socks5://127.0.0.1:1080`)    |
| `--tor`             | Route through Tor (requires Tor on port 9050)            |
| `--retries N`       | Retry failed requests N times (default: 1)               |

### Data management

| Flag                 | Description                                       |
|----------------------|---------------------------------------------------|
| `--update`           | Fetch latest data from Sherlock + Maigret          |
| `--list-sites`       | List all available sites with URL patterns         |
| `--list-categories`  | List all categories with site counts              |
| `--stats`            | Show data source breakdown and category stats     |

### Misc

| Flag            | Description                  |
|-----------------|------------------------------|
| `-V, --version` | Show version and exit        |
| `-h, --help`    | Show help message and exit   |

---

## Filtering

### By category

Only check dating and social media sites:

```bash
wmn target_user --category dating,social
```

Exclude gaming sites from the scan:

```bash
wmn target_user --exclude-category gaming
```

### By specific site

Check only specific sites (partial name match):

```bash
wmn target_user --site Instagram --site Twitter --site Tinder
```

### Combining filters

Scan dating and finance categories with NSFW included, verbose output:

```bash
wmn target_user --category dating,finance --nsfw -v
```

---

## Output & Export

### Terminal output

By default, results are displayed in the terminal with:
- A progress bar showing scan completion
- Real-time green checkmarks (✓) for found accounts
- A summary table grouped by category at the end

### JSON export

```bash
wmn johndoe --output json
# Creates: johndoe.json
```

The JSON file contains:
- `username` — the searched username
- `timestamp` — ISO 8601 timestamp
- `found_count` — number of accounts found
- `total_checked` — number of sites checked
- `results` — array of found accounts (site, url, category, response_time)
- `all_results` — complete results including not-found and errors

### CSV export

```bash
wmn johndoe --output csv
# Creates: johndoe.csv
```

Columns: `site, url, status, http_code, category, response_time, error`

### HTML report

```bash
wmn johndoe --output html
# Creates: johndoe.html
```

Generates a self-contained dark-themed HTML report with:
- Stats cards (found, checked, errors)
- Clickable links to all discovered profiles
- Grouped by category

### Custom output path

```bash
wmn johndoe --output json --output-file /path/to/report.json
```

---

## Connection Options

### Adjusting timeout

For slow connections or sites behind Cloudflare:

```bash
wmn johndoe --timeout 30
```

For faster scans where you accept some timeouts:

```bash
wmn johndoe --timeout 8
```

### Adjusting concurrency

More workers = faster but more aggressive:

```bash
wmn johndoe --workers 200
```

Fewer workers for stealth or rate-limited networks:

```bash
wmn johndoe --workers 20
```

### Using a proxy

HTTP proxy:

```bash
wmn johndoe --proxy http://proxy.example.com:8080
```

SOCKS5 proxy:

```bash
wmn johndoe --proxy socks5://127.0.0.1:1080
```

### Using Tor

Requires Tor to be installed and running on port 9050:

```bash
# Start Tor first
tor &

# Route all requests through Tor
wmn johndoe --tor
```

Note: Tor significantly reduces speed. Consider reducing workers:

```bash
wmn johndoe --tor --workers 10 --timeout 30
```

### Retries

For unreliable connections:

```bash
wmn johndoe --retries 3
```

---

## Data Management

### Updating site data

Fetch the latest site definitions from Sherlock and Maigret projects:

```bash
wmn --update
```

This caches data in `~/.cache/whatsmyname/`. Run periodically to stay current.

### Viewing available sites

```bash
wmn --list-sites
```

Shows a table of all sites with their name, category, and URL pattern.

### Viewing categories

```bash
wmn --list-categories
```

Shows all categories with the number of sites in each.

### Viewing data statistics

```bash
wmn --stats
```

Shows a breakdown by data source (wmn, extended, sherlock, maigret) and by category.

### Chaining update with a scan

```bash
wmn --update johndoe
```

This updates data first, then runs the scan — useful for ensuring fresh data.

---

## Categories

After running `wmn --update`, the following categories are available:

| Category     | Description                                    | Example sites                           |
|-------------|------------------------------------------------|-----------------------------------------|
| `social`     | Social networks and communities                | Facebook, Instagram, Mastodon, VK       |
| `dating`     | Dating and hookup platforms                    | Tinder, Bumble, Hinge, OkCupid         |
| `finance`    | Finance, crypto, trading, money transfer       | Binance, Coinbase, Venmo, PayPal        |
| `gaming`     | Gaming platforms and communities               | Steam, Xbox, PlayStation, Roblox        |
| `coding`     | Developer tools and platforms                  | GitHub, GitLab, Stack Overflow, npm     |
| `tech`       | Technology communities and forums              | XDA, Cloudflare, Discourse forums       |
| `shopping`   | E-commerce and marketplaces                    | eBay, Etsy, Poshmark, Mercari          |
| `blog`       | Blogging and writing platforms                 | Medium, Substack, WordPress, Ghost      |
| `images`     | Photo and image sharing                        | Flickr, Imgur, Pixelfed, DeviantArt     |
| `video`      | Video and streaming platforms                  | YouTube, Twitch, Kick, Odysee          |
| `music`      | Music platforms and communities                | Spotify, SoundCloud, Bandcamp           |
| `hobby`      | Hobbies, interests, niche communities          | Goodreads, BoardGameGeek, Strava       |
| `art`        | Art communities and portfolios                 | Behance, Dribbble, pixiv               |
| `business`   | Professional and business networks             | LinkedIn, Crunchbase, Upwork           |
| `health`     | Health and fitness platforms                   | Strava, Fitbit, AllTrails              |
| `news`       | News sites with user profiles                  | Reuters, Bloomberg, The Guardian        |
| `political`  | Political platforms and communities            | Parler, Gab, Truth Social              |
| `misc`       | Miscellaneous / uncategorized                  | Various niche sites                     |
| `archived`   | Sites that are no longer active                | Historical references                   |
| `xx NSFW xx` | Adult/NSFW content (excluded by default)       | OnlyFans, Fansly, adult cam sites       |

---

## Deception-Focused Investigations

This tool has comprehensive coverage of sites where someone acting deceptively would likely maintain accounts. Here are targeted scan strategies:

### Romance scam investigation

```bash
wmn suspect_user --category dating,social --nsfw -v --output html
```

Covers: Tinder, Bumble, Hinge, OkCupid, Badoo, Ashley Madison, Seeking.com, Grindr, social platforms, and adult sites.

### Financial fraud / crypto scam

```bash
wmn suspect_user --category finance --output json
```

Covers: Binance, Coinbase, KuCoin, Bybit, OKX, Bitcoin forums, OpenSea, Rarible, PayPal, Venmo, Cash App, plus 60+ DeFi community forums.

### Catfishing / fake identity

```bash
wmn suspect_user --category social,dating,images --nsfw --output html
```

Check link-in-bio sites, social media, dating platforms, and image sharing sites where fake profiles are created.

### Marketplace fraud

```bash
wmn suspect_user --category shopping --output csv
```

Covers: eBay, Mercari, Poshmark, Depop, StockX, OfferUp, Vinted, Grailed, and more.

### Alt-social / extremism

```bash
wmn suspect_user --category political,social --nsfw -v
```

Covers: Gab, Truth Social, Parler, Gettr, Rumble, BitChute, Minds, plus Mastodon instances, Pleroma, and fringe forums.

### Full comprehensive scan

```bash
wmn suspect_user --nsfw -v --output html --workers 200
```

Checks every single site in the database.

---

## Advanced Usage

### Running as a Python module

```bash
python -m whatsmyname johndoe
```

### Scripting with JSON output

```bash
wmn johndoe --output json --no-banner --no-color
# Then parse johndoe.json with jq, Python, etc.
```

Extract just the found URLs:

```bash
wmn johndoe --output json --no-banner
cat johndoe.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['results']:
    print(r['url'])
"
```

### Regenerating the extended site database

If you modify `scripts/generate_sites.py` to add custom sites:

```bash
python3 scripts/generate_sites.py
```

This regenerates `whatsmyname/data/extended_sites.json`.

### Using as a library

```python
import asyncio
from whatsmyname.checker import check_username, CheckerConfig
from whatsmyname.data_manager import load_all_local

sites = load_all_local()
config = CheckerConfig(timeout=10, max_workers=50)

results = asyncio.run(check_username("johndoe", sites, config))

found = [r for r in results if r.status.value == "found"]
for r in found:
    print(f"{r.site_name}: {r.url}")
```

---

## Troubleshooting

### "No sites match your filters"

- Check spelling of category names: `wmn --list-categories`
- NSFW sites are excluded by default — add `--nsfw` if needed

### Scan is very slow

- Increase workers: `--workers 200`
- Decrease timeout: `--timeout 8`
- The first run after `--update` may be slower due to cold caches

### Many timeouts or errors

- Increase timeout: `--timeout 30`
- Add retries: `--retries 3`
- Some sites block automated requests — this is expected
- Use `--verbose` to see which sites are failing and why

### SSL errors

- The tool disables strict SSL verification by default to handle self-signed certs
- If you still see SSL errors, try using a proxy: `--proxy http://proxy:8080`

### Tor connection refused

- Make sure Tor is running: `tor &` or via Tor Browser
- Default SOCKS port is 9050 (not 9150 from Tor Browser)
- Install aiohttp-socks: `pip install aiohttp-socks`

### "wmn: command not found"

- Make sure you installed with `pip install -e .` in the repo directory
- Check that your pip bin directory is in PATH:
  ```bash
  python3 -m whatsmyname --version
  ```
- Try: `pip install -e .` again

### Data sources return 0 sites

- Run `wmn --update` to re-fetch
- Check internet connectivity
- Remote sources (Sherlock/Maigret) require GitHub access

---

## Data Sources

| Source      | Sites | Description                                          |
|-------------|-------|------------------------------------------------------|
| WhatsMyName | 731   | Core verified sites from the WMN project             |
| Extended    | 1,076 | Curated additions: Fediverse, forums, dating, crypto |
| Sherlock    | ~478  | Fetched from sherlock-project/sherlock on GitHub      |
| Maigret     | ~3,013| Fetched from soxoj/maigret on GitHub                 |
| **Total**   | **~4,387** | **After deduplication across all sources**      |

Run `wmn --update` periodically to fetch the latest data from Sherlock and Maigret.

---

## RECON — Unified Multi-Tool Search

The `recon` command is a master orchestrator that triggers **every installed OSINT tool in parallel** from a single search. One input — username, email, or phone — fans out across all applicable tools simultaneously.

### Installed tools (11 total)

**Username enumeration (6 tools):**
- **wmn** — WhatsMyName, 4,387+ sites
- **sherlock** — Sherlock Project, ~400 sites
- **maigret** — Maigret, ~3,000 sites with deep detection
- **social-analyzer** — Social Analyzer, 900+ sites
- **socialscan** — GitHub, GitLab, Instagram, Pinterest, Reddit, Twitter, Tumblr
- **nexfil** — NExfil OSINT username finder

**Email reconnaissance (4 tools):**
- **holehe** — checks which services an email is registered on
- **h8mail** — email breach/leak data lookup
- **socialscan** — email availability on major platforms
- **theHarvester** — gathers emails, hosts, URLs from public sources

**Phone number intelligence (2 tools):**
- **phoneinfoga** — advanced phone number OSINT (carrier, location, search links)
- **ignorant** — checks phone registrations on social platforms

### Quick start

```bash
# Username search — triggers all 6 username tools + email tools on variants
recon johndoe

# Email search — triggers holehe, h8mail, socialscan, theHarvester
recon johndoe@gmail.com

# Phone search — triggers phoneinfoga, ignorant
recon +15551234567
```

### How it works

1. **Auto-detects input type** — username, email, or phone (override with `--type`)
2. **Runs all applicable tools in parallel** as subprocesses
3. **Parses output** from each tool (JSON where available, stdout fallback)
4. **Deduplicates findings** across tools
5. **Displays a unified report** with live progress, tool breakdown, and categorized results

### Email expansion (username searches)

For username searches, `recon` automatically generates email variants (e.g. `johndoe@gmail.com`, `@yahoo.com`, `@outlook.com`, `@hotmail.com`, `@protonmail.com`, `@icloud.com`, `@aol.com`) and runs **holehe**, **h8mail**, and **socialscan** against each one. This dramatically increases coverage.

Disable with `--no-email-expand`.

### All flags

```
recon <target> [options]

  target                    Username, email, or phone number
  --type TYPE               Override auto-detection (username, email, phone)
  --tools TOOLS             Comma-separated list of specific tools to run
  --no-email-expand         Skip email variant generation for username searches
  --timeout SECONDS         Override per-tool timeout
  -o, --output FORMAT       Export report: json, csv, or html
  --output-file PATH        Custom output file path
  --no-banner               Skip ASCII banner
  --list-tools              Show all tools and their install status
  -V, --version             Show version
```

### Examples

```bash
# Full username scan with HTML report
recon suspect_user --output html

# Only run wmn and sherlock
recon suspect_user --tools wmn,sherlock

# Phone lookup
recon +447911123456 --output json

# Email with custom timeout
recon target@protonmail.com --timeout 60 --output html

# Username scan without email expansion (faster)
recon suspect_user --no-email-expand

# Check which tools are available
recon --list-tools
```

### Output format

The unified JSON report contains:

```json
{
  "target": "johndoe",
  "input_type": "username",
  "timestamp": "2024-01-01T00:00:00+00:00",
  "summary": {
    "total_unique_accounts": 47,
    "tools_completed": 8,
    "tools_failed": 0
  },
  "tools": [
    {"name": "wmn", "status": "completed", "findings": 23, "elapsed": 45.2},
    {"name": "sherlock", "status": "completed", "findings": 18, "elapsed": 30.1}
  ],
  "findings": [
    {"source": "wmn", "site": "Instagram", "url": "https://instagram.com/johndoe", "category": "social"},
    {"source": "sherlock", "site": "GitHub", "url": "https://github.com/johndoe", "category": "social"}
  ]
}
```

### Installing additional tools

All tools were installed via pip:

```bash
pip install sherlock-project   # Sherlock username search
pip install maigret            # Maigret deep username search
pip install social-analyzer    # Social Analyzer 900+ sites
pip install socialscan          # Username/email availability
pip install nexfil              # NExfil username finder
pip install holehe              # Email registration checker
pip install h8mail              # Email breach lookup
pip install ignorant            # Phone social media checker
# phoneinfoga requires separate install (Go binary)
# theHarvester: pip install theHarvester
```

Run `recon --list-tools` to verify what's installed.
