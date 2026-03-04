<h1 align="center">🔴 Project RECON</h1>
<h3 align="center">Rapid Evidence Collection & OSINT Network</h3>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/platform-macOS-black?style=flat-square&logo=apple" alt="Platform"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-cc0000?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <img src="https://img.shields.io/badge/version-3.0.0-ff0000?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/tools-45%2B-8b0000?style=flat-square" alt="Tools">
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-333333?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <b>One search. Every tool. No mercy.</b><br>
  <sub>A unified forensics & OSINT workbench that orchestrates 40+ tools through a single CLI.</sub>
</p>

---

## What Is This?

Project RECON is a command-line investigation workbench that replaces the need to manually run dozens of separate OSINT and forensics tools. Type one command, and RECON automatically:

- **Detects** your input type (username, email, or phone)
- **Selects** the right tools for that input
- **Runs them in parallel** with live status display
- **Deduplicates and correlates** findings
- **Exports** unified reports (JSON, CSV, HTML, PDF, Markdown)
- **Tracks** investigations with sessions, chain-of-custody, and evidence bags

Built on top of [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) and extending it from a data file into a full investigation platform.

---

## Features

### Core Engine
- **Unified orchestration** of 40+ tools across 17 categories
- **Auto-detection** of input type (username / email / phone number)
- **Parallel execution** with real-time progress dashboard
- **Smart deduplication** across overlapping tool results
- **Template-based scanning** — 9 predefined profiles for common investigation types
- **Workflow system** — 8 step-by-step investigation workflows
- **Plugin architecture** — extend with your own tools via Python plugins

### Investigation Features
- **Session tracking** — resume investigations, compare over time
- **Chain of custody** — timestamped action logs, SHA-256 hashing
- **Evidence bags** — forensically-sound output packaging
- **Exposure scoring** — 1-100 risk rating with category breakdown
- **Cross-correlation** — automatic finding linkage across tools

### Operational Security
- **VPN detection** — refuse to run if unprotected
- **OpSec warnings** — flag tools that leave traces
- **Tor routing** — built-in SOCKS5 proxy support
- **Rate limiting + jitter** — avoid detection patterns

### Learning & Discovery
- **`recon learn <tool>`** — beginner-friendly guides with examples
- **`recon suggest <tool>`** — intelligent "what to run next" recommendations
- **`recon categories`** — browse tools by forensics category
- **`recon inventory`** — full system audit of installed tools

---

## Tool Categories

```
Username Enumeration    Network Forensics       Memory Forensics
Email Investigation     Wireless Security       Steganography
Phone Lookup            Password Recovery       Document Analysis
Social Engineering      Disk Forensics          Reverse Engineering
Vulnerability Scanning  OSINT Frameworks        Metadata Extraction
Web Application         Face Recognition        iOS Forensics
Relationship Investigation (SPOTLIGHT)
```

---

## Installation

### One-Command Install (Portable Drive)

Plug in the drive, open Terminal:

```bash
bash /Volumes/YOUR_DRIVE/RECON_WorkBench/install.sh
```

This will:
1. Copy Project RECON to `~/RECON_WorkBench`
2. Create an isolated Python virtual environment
3. Install all 40+ OSINT tools
4. Add `recon` to your PATH
5. Set up weekly auto-updates

### Install from GitHub

```bash
git clone https://github.com/newbiehackler/project-recon.git
cd project-recon
bash install.sh
```

### Manual Install (Developer)

```bash
git clone https://github.com/newbiehackler/project-recon.git
cd project-recon
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install sherlock-project maigret social-analyzer socialscan holehe h8mail nexfil
```

### Requirements

- **macOS 12+** (Monterey or newer)
- **Python 3.10+**
- **Homebrew** (recommended, for forensics tools like nmap, wireshark, etc.)

---

## Quick Start

```bash
# Search a username across all tools
recon johndoe

# Search an email
recon johndoe@gmail.com

# Search a phone number
recon +15551234567

# Deep scan with suggestions
recon johndoe --deep --discover

# Use a predefined template
recon johndoe --template full-osint

# Track in a session
recon johndoe --session case001 --examiner "Agent X"

# Export to JSON
recon johndoe -o json

# Dry run (see what would execute)
recon johndoe --dry-run
```

---

## Subcommands

```
recon <target>                  Search a username/email/phone
recon inventory                 Full system tool audit
recon learn <tool>              Beginner-friendly tool guide
recon suggest <tool>            What to run next and why
recon categories                Browse tools by category
recon workflows                 Investigation workflow templates
recon templates                 Predefined scan profiles
recon update                    Update all tools & dependencies
recon shell                     Interactive investigation REPL
```

### Plugin Marketplace Commands

```
recon plugins                   List installed plugins
recon plugins search [query]    Browse marketplace
recon plugins install <name>    Install a plugin (--key KEY for paid)
recon plugins uninstall <name>  Remove a plugin
recon plugins create <name>     Scaffold a new plugin
recon plugins validate <file>   Validate before submission
recon plugins submit <file>     Submit to marketplace via GitHub Issue
```

### All Flags

```
Core:
  --type username|email|phone   Override input auto-detection
  --tools wmn,sherlock,...      Run only specific tools
  --timeout 120                 Per-tool timeout in seconds
  -o json|csv|html              Export report format
  --output-file report.json     Custom output path
  --no-banner                   Skip the ASCII banner
  --list-tools                  Show all tools + install status
  -V, --version                 Show version

Scan Control:
  --deep                        All tools, 2x timeouts
  --quick                       Top 3 fastest tools only
  --passive                     Non-intrusive tools only
  --dry-run                     Preview without executing
  --template full-osint         Use predefined scan profile
  --parallel 5                  Limit concurrent tools
  --retries 2                   Retry failed tools
  --proxy http://127.0.0.1:8080 Route through proxy
  --tor                         Route through Tor

Input:
  -f targets.txt                Read targets from file
  --stdin                       Read from stdin
  --no-email-expand             Skip email variant generation

Output:
  --raw                         Show raw tool stdout
  --save-raw ./raw_output       Save raw outputs to directory
  --no-color                    Plain text (no ANSI colors)
  --open                        Auto-open HTML report in browser
  --pdf                         Export as PDF
  --markdown                    Export as Markdown

Investigation:
  --session case001             Create/resume named session
  --case-id CASE-2024-001       Tag with case ID
  --notes "initial recon"       Attach notes
  --examiner "Agent X"          Tag examiner name
  --discover                    Suggest complementary tools after scan
  --enrich                      Auto-enrich findings (DNS, whois)
  --score                       Calculate exposure risk score (1-100)
  --correlate                   Cross-reference across tools
  --diff previous_scan.json     Compare against prior scan

Chain of Custody:
  --evidence-bag ./evidence     Forensic evidence bag directory
  --chain-of-custody            Timestamped action logging
  --hash-verify                 SHA-256 hash all outputs

OpSec:
  --opsec-check                 Warn about trace-leaving tools
  --vpn-check                   Block if no VPN detected
  --rate-limit 5                Max requests/second
  --jitter                      Random delays between tools

Automation:
  --webhook https://...         POST results when done
  --notify                      macOS desktop notification
  --on-finding "cmd {}"         Run command per finding
  --filter category=social      Filter results

Learning:
  --cheatsheet nmap             Quick reference for a tool
  --explain "chain of custody"  Explain a forensics concept
```

---

## Architecture

```
RECON_WorkBench/
├── install.sh              # One-command portable installer
├── update.sh               # Auto-update script
├── uninstall.sh            # Clean removal
├── WhatsMyName/            # Core project
│   ├── pyproject.toml      # Package config
│   ├── whatsmyname/
│   │   ├── recon_cli.py    # Main CLI entry point
│   │   ├── orchestrator.py # Tool execution engine
│   │   ├── tool_catalog.py # 40+ tool definitions
│   │   ├── workflows.py    # Investigation workflows
│   │   ├── templates.py    # Scan profiles
│   │   ├── sessions.py     # Session persistence
│   │   ├── evidence.py     # Chain of custody
│   │   ├── enrichment.py   # Finding enrichment
│   │   ├── plugin_loader.py# Plugin system
│   │   └── shell.py        # Interactive REPL
│   └── wmn-data.json       # 4,000+ site database
├── tools/                  # Bundled tools
│   ├── blackbird/          # Username search (600+ sites)
│   ├── cupidcr4wl/         # Dating/adult platform OSINT
│   ├── compreface/         # Face recognition (Docker)
│   ├── untappd-scraper/    # Social behavior intelligence
│   ├── 4n6notebooks/       # iOS forensic Jupyter notebooks
│   ├── keychain-decrypter/ # iOS keychain decryption
│   └── osint-tools-cli/    # 1,000+ OSINT tool browser (Rust TUI)
└── .recon/                 # User data (portable)
    ├── plugins/
    ├── sessions/
    └── evidence/
```

---

## Configuration

Project RECON stores user data in `~/.recon/`:

```
~/.recon/
├── plugins/                # Custom tool plugins (.py)
├── sessions/               # Investigation sessions (.json)
├── spotlight_plugins/      # SPOTLIGHT module plugins
├── evidence/               # Evidence bags
├── exports/                # Exported reports
└── logs/                   # Auto-update logs
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RECON_HOME` | Installation directory | `~/RECON_WorkBench` |

---

## Updating

### Manual Update

```bash
recon update              # Update everything
recon update --pip        # Only Python tools
recon update --brew       # Only Homebrew tools
recon update --bundled    # Only git-cloned tools
```

### Auto-Update

The installer sets up a weekly launchd job (Monday 3:00 AM) that silently updates all tools. Logs are saved to `~/.recon/logs/`.

To disable:
```bash
launchctl unload ~/Library/LaunchAgents/dev.recon.autoupdate.plist
```

---

## Extending with Plugins

Create a Python file in `~/.recon/plugins/`:

```python
# ~/.recon/plugins/my_tool.py
RECON_TOOLS = [
    {
        "name": "my-scanner",
        "command": "my-scanner",
        "description": "My custom scanning tool",
        "input_types": ["username"],
        "args_template": ["{target}"],
    }
]
```

RECON automatically loads it on next run.

---

## Uninstalling

```bash
bash ~/RECON_WorkBench/uninstall.sh
```

This removes RECON, launchers, auto-update jobs, and shell config entries. Your pip/brew tools remain untouched.

---

## Recommended Future Integrations

Based on extensive research across GitHub, security conferences, and DFIR communities, these open-source tools would be high-value additions to RECON. Organized by tier and category.

### Tier 1 — Must-Have (Fills Critical Gaps)

**OSINT Automation & Frameworks**
- [SpiderFoot](https://github.com/smicallef/spiderfoot) — 200+ modules, auto-correlates IPs/domains/emails/usernames, web UI + CLI, Python, MIT license
- [Recon-ng](https://github.com/lanmaster53/recon-ng) — Modular CLI reconnaissance framework with workspaces, API integrations, and built-in reporting
- [Reconftw](https://github.com/six2dez/reconftw) — Automated recon pipeline that orchestrates Amass + Subfinder + Nuclei + httpx + dozens more into a single workflow
- [BBOT](https://github.com/blacklanternsecurity/bbot) — Next-gen OSINT automation for hackers; recursive scanning, event-driven architecture, 100+ modules

**Subdomain & Attack Surface Discovery**
- [Amass](https://github.com/owasp-amass/amass) (OWASP) — Gold standard for subdomain discovery, network mapping, and external asset enumeration
- [Subfinder](https://github.com/projectdiscovery/subfinder) — Fast passive subdomain enumeration using 45+ data sources (Go, by ProjectDiscovery)
- [httpx](https://github.com/projectdiscovery/httpx) — Fast multi-purpose HTTP toolkit for probing web servers, tech detection, status codes
- [Nuclei](https://github.com/projectdiscovery/nuclei) — Fast vulnerability scanner based on YAML templates; 7,000+ community templates
- [Katana](https://github.com/projectdiscovery/katana) — Next-generation crawling and spidering framework by ProjectDiscovery

**Memory & Disk Forensics**
- [Volatility 3](https://github.com/volatilityfoundation/volatility3) — Extract processes, network connections, and malware from RAM dumps — essential for DFIR
- [Autopsy](https://github.com/sleuthkit/autopsy) / [The Sleuth Kit](https://github.com/sleuthkit/sleuthkit) — Industry-standard disk image analysis, file carving, timeline generation
- [Shodan CLI](https://cli.shodan.io/) — Search internet-connected devices, exposed services, and vulnerabilities from the terminal

### Tier 2 — High Value

**Link Analysis & Visualization**
- [Maltego CE](https://www.maltego.com/maltego-community/) — Visual relationship mapping between entities — free community edition with 58+ data sources
- [OpenCTI](https://github.com/OpenCTI-Platform/opencti) — Open-source threat intelligence platform; structured knowledge graph with STIX2 support
- [MISP](https://github.com/MISP/MISP) — Malware Information Sharing Platform; threat intelligence sharing with correlation engine

**Social Media & People OSINT**
- [Osintgram](https://github.com/Datalux/Osintgram) — Interactive shell for deep Instagram recon (followers, geolocations, stories, comments, media)
- [Instaloader](https://github.com/instaloader/instaloader) — Download Instagram posts, stories, highlights, metadata, and profile data (11.7k stars)
- [Twint](https://github.com/twintproject/twint) — Advanced Twitter scraping without API; followers, tweets, geolocation, email hunting
- [SocialPwned](https://github.com/MrTuxx/SocialPwned) — Cross-platform email harvesting from Instagram/LinkedIn/Twitter + breach checking via PwnDB/Dehashed/GHunt
- [CrossLinked](https://github.com/m8sec/CrossLinked) — LinkedIn enumeration via search engine scraping to extract employee names for email generation
- [DaProfiler](https://github.com/daprofiler/DaProfiler) — Recover addresses, social accounts, emails, phone numbers, and jobs using web scraping + Google dorking
- [Tookie-OSINT](https://github.com/Alfredredbird/tookie-osint) — Advanced OSINT gathering tool that finds social media accounts across platforms (1.7k stars)

**Google & Email Intelligence**
- [GHunt](https://github.com/mxrch/GHunt) — Investigate Google accounts (emails, reviews, photos, maps contributions, calendar events)
- [Mosint](https://github.com/alpkeskin/mosint) — Automated email OSINT tool for gathering information about email addresses
- [Quidam](https://github.com/megadose/Quidam) — Retrieve information via forgotten-password functions on websites; has Maltego transforms

**Phone Intelligence**
- [Moriarty-Project](https://github.com/AzizKpln/Moriarty-Project) — Web-based phone number investigation tool with 6+ features and multi-source lookup

**Reverse Engineering & Binary Analysis**
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra) — NSA's open-source SRE suite with decompiler, far more powerful than objdump/lldb alone

**Web Recon & Crawling**
- [Photon](https://github.com/s0md3v/Photon) — Incredibly fast OSINT crawler that extracts URLs, emails, social accounts, files, and JS
- [web-check](https://github.com/Lissy93/web-check) — All-in-one OSINT tool for analyzing any website (DNS, SSL, headers, tech stack, security)
- [Gobuster](https://github.com/OJ/gobuster) — Directory/file, DNS and VHost busting tool written in Go
- [Feroxbuster](https://github.com/epi052/feroxbuster) — Fast, recursive content discovery tool written in Rust
- [waybackurls](https://github.com/tomnomnom/waybackurls) — Fetch all URLs the Wayback Machine knows about for a domain
- [gau](https://github.com/lc/gau) — Fetch known URLs from AlienVault, Wayback Machine, and Common Crawl

**Document & Metadata Extraction**
- [Metagoofil](https://github.com/laramies/metagoofil) — Extract metadata from public documents (PDFs, DOCs) found on target domains
- [FOCA](https://github.com/ElevenPaths/FOCA) — Automated document harvester; extracts internal org structures from Google/Bing/DuckDuckGo
- [Imago Forensics](https://github.com/redaelli/imago-forensics) — Extract digital evidence from images recursively for forensic investigations

**Internet-Wide Scanning**
- [Censys CLI](https://github.com/censys/censys-python) — Query internet-wide scan data for hosts, certificates, and services
- [IVRE](https://github.com/ivre/ivre) — Network recon framework; build your own Shodan/ZoomEye/Censys alternative
- [Findomain](https://github.com/Edu4rdSHL/findomain) — Fast domain recon with screenshotting, port scanning, and subdomain monitoring

**OSINT Frameworks & Package Managers**
- [sn0int](https://github.com/kpcyrd/sn0int) — Semi-automatic OSINT framework with built-in package manager for community modules
- [ReconSpider](https://github.com/bhavsec/reconspider) — Advanced OSINT framework for scanning IPs, emails, websites, organizations with dashboard visualization
- [iKy](https://github.com/kennbroorg/iKy) — OSINT tool that collects information from email and presents it as a visual dashboard

### Tier 3 — Specialized & Advanced

**Dark Web OSINT**
- [OnionSearch](https://github.com/megadose/OnionSearch) — Scrape URLs from multiple .onion search engines for dark web investigations
- [TorBot](https://github.com/DedSecInside/TorBot) — Dark web OSINT tool; crawls .onion sites, extracts emails, and maps dark web topology

**Cryptocurrency & Blockchain Investigation**
- [Orbit](https://github.com/s0md3v/Orbit) — Draws relationships between crypto wallets with recursive transaction history crawling
- [Maltego BTC/ETH](https://www.maltego.com/) — Maltego supports Bitcoin and Ethereum address entities for transaction mapping

**Geolocation OSINT**
- [Creepy](https://github.com/ilektrojohn/creepy) — Geolocation OSINT from social networks; presents on map, export to CSV/KML for Google Maps
- [ShadowFinder](https://github.com/bellingcat/ShadowFinder) — Find possible geolocations from shadow analysis in images

**Digital Forensics (Advanced)**
- [Dissect](https://github.com/fox-it/dissect) — DFIR framework to parse forensic artefacts from disk/file formats at scale — by Fox-IT/NCC Group
- [Hayabusa](https://github.com/Yamato-Security/hayabusa) — Sigma-based threat hunting and fast forensics timeline generator for Windows event logs (Rust)
- [mac_apt](https://github.com/ydkhatri/mac_apt) — macOS DFIR tool to extract artifacts from full disk images
- [IPED](https://github.com/sepinf-inc/IPED) — Brazilian Federal Police forensic tool — processes disk images at 400GB/hr, 40+ carving formats
- [Zeek](https://github.com/zeek/zeek) — Deep network traffic analysis framework; generates detailed activity logs for forensic correlation
- [Traceeshark](https://github.com/aquasecurity/traceeshark) — Wireshark plugin adding kernel-level event analysis and behavioral detection
- [Forensix](https://github.com/ChmaraX/forensix) — Google Chrome forensic tool to process, analyze and visualize browsing artifacts
- [firefox_decrypt](https://github.com/unode/firefox_decrypt) — Extract passwords from Firefox/Thunderbird/Seabird profiles
- [Cameradar](https://github.com/Ullaakut/cameradar) — Hack into RTSP video surveillance cameras for security auditing
- [Linux Explorer](https://github.com/intezer/linux-explorer) — Easy-to-use live forensics toolbox for Linux endpoints

**Google Dorking & Fuzzing**
- [pagodo](https://github.com/opsdisk/pagodo) — Automate Google Hacking Database queries for target reconnaissance
- [GooFuzz](https://github.com/m3n0sd0n4ld/GooFuzz) — OSINT fuzzing tool that enumerates directories, files, subdomains via advanced Google dorking

**GitHub & Code OSINT**
- [commit-stream](https://github.com/x1sec/commit-stream) — Find GitHub repos by extracting commit logs in real-time from the GitHub Event API
- [github-dorks](https://github.com/techgaun/github-dorks) — CLI tool to scan GitHub repos/organizations for potential sensitive information leaks

**Vulnerability Scanning**
- [Raccoon](https://github.com/evyatarmeged/Raccoon) — High performance offensive recon and vulnerability scanning tool
- [Sn1per](https://github.com/1N3/Sn1per) — Automated pentest framework with attack surface management and vulnerability scanning

> **50+ tools** across 15+ categories. To request an integration, open an issue on GitHub or submit a plugin via `recon plugins create`.

---

## Roadmap

- [ ] **SPOTLIGHT Module** — Relationship investigation with GUI, phone backup forensics, timeline/pattern detection, red flag scoring
- [ ] **Web Dashboard** — Browser-based investigation interface
- [ ] **Cross-platform** — Linux support
- [x] **Plugin Marketplace** — Community tool sharing with 70/30 revenue split
- [ ] **API Mode** — REST API for programmatic access
- [ ] **Tier 1 Tool Integrations** — SpiderFoot, Recon-ng, Reconftw, BBOT, Amass, Subfinder, httpx, Nuclei, Katana, Volatility, Autopsy/TSK, Shodan CLI
- [ ] **Tier 2 Social & People OSINT** — Osintgram, Instaloader, Twint, SocialPwned, CrossLinked, GHunt, Tookie-OSINT
- [ ] **Tier 2 Web & Infrastructure** — Maltego CE, OpenCTI, MISP, Photon, web-check, Censys CLI, IVRE
- [ ] **Tier 3 Dark Web & Crypto** — OnionSearch, TorBot, Orbit
- [ ] **Tier 3 Advanced Forensics** — Dissect, Hayabusa, Zeek, IPED, mac_apt, Traceeshark

---

## Support the Project

Project RECON is free and open source. If it saves you time, consider supporting development:

<p align="center">
  <a href="https://github.com/sponsors/newbiehackler"><img src="https://img.shields.io/badge/GitHub_Sponsors-Support-ff0000?style=for-the-badge&logo=github" alt="GitHub Sponsors"></a>
  <a href="https://venmo.com/u/Travis-LeFevre-3"><img src="https://img.shields.io/badge/Venmo-Tip-3D95CE?style=for-the-badge&logo=venmo" alt="Venmo"></a>
  <a href="https://cash.app/$Travis0706"><img src="https://img.shields.io/badge/Cash_App-Tip-00C244?style=for-the-badge&logo=cashapp" alt="Cash App"></a>
</p>

### Plugin Marketplace

Build and sell your own RECON plugins. **70/30 revenue split** — you keep 70%.

```bash
# Browse available plugins
recon plugins search

# Install a plugin
recon plugins install social-deep-dive

# Create your own plugin
recon plugins create my-scanner

# Validate before submitting
recon plugins validate my_scanner.py

# Submit to the marketplace
recon plugins submit my_scanner.py

# Paid plugins require a license key
recon plugins install premium-tool --key RECON-PREM-abc123
```

**For plugin developers:**
- Write a plugin → validate → submit → earn money on every install
- Free or paid tiers — you choose the price
- Full guide: [Plugin Development Guide](docs/plugin-development.md)

**For investigators:**
- Browse community plugins: `recon plugins search`
- One-command install: `recon plugins install <name>`
- 3 free starter plugins available now

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- Add new tool integrations
- Submit site detections for WMN data
- Write plugins
- Report bugs or suggest features
- Improve documentation

---

## Credits

Built on top of [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) by [Micah Hoffman](https://webbreacher.com). Project RECON extends WMN into a full investigation platform while maintaining backward compatibility with the original data format.

---

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](LICENSE.md).

---

 