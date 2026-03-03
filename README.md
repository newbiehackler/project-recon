<h1 align="center">🔴 Project RECON</h1>
<h3 align="center">Rapid Evidence Collection & OSINT Network</h3>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/platform-macOS-black?style=flat-square&logo=apple" alt="Platform"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-cc0000?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <img src="https://img.shields.io/badge/version-3.0.0-ff0000?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/tools-40%2B-8b0000?style=flat-square" alt="Tools">
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
Web Application         Relationship Investigation (SPOTLIGHT)
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
├── tools/                  # Bundled git-based tools
│   ├── blackbird/
│   └── cupidcr4wl/
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

## Roadmap

- [ ] **SPOTLIGHT Module** — Relationship investigation with GUI, phone backup forensics, timeline/pattern detection, red flag scoring
- [ ] **Web Dashboard** — Browser-based investigation interface
- [ ] **Cross-platform** — Linux support
- [x] **Plugin Marketplace** — Community tool sharing with 70/30 revenue split
- [ ] **API Mode** — REST API for programmatic access

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

 