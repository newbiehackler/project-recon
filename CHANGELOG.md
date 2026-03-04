# Changelog

All notable changes to Project RECON are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [3.1.0] — 2026-03-04

### Added
- **CompreFace integration** — self-hosted face recognition (detect, recognize, verify faces) via Docker + REST API wrapper
- **untappdScraper integration** — social behavior intelligence from Untappd.com (drinking patterns, geolocation, friend networks)
- **4n6notebooks integration** — Jupyter forensic notebooks for iOS (SQLCipher decrypt, Signal parsing, ProtonMail recovery)
- **iOS Keychain Decrypter integration** — decrypt saved passwords, WiFi creds, app tokens from jailbroken iOS devices
- **OSINT Tools CLI integration** — interactive Rust TUI browser for 1,000+ OSINT tools from Cipher387's collection
- All 5 new tools have extensive `--help` output, launcher wrappers, catalog entries, and auto-update support
- Tool count increased from 40+ to 45+ across 17+ categories
- New categories active: Face Recognition & Image Intel, iOS Forensics

### Changed
- `install.sh` now installs and configures all 5 new bundled tools with dependency management
- `update.sh` now rebuilds Rust and C binaries during auto-updates
- README updated with new architecture diagram and tool count

---

## [3.0.0] — 2026-03-01

### Added
- **Project RECON rebrand** — blood-red tactical banner, skull crossbones, gradient status bars
- **Unified CLI** (`recon`) — single entry point orchestrating 40+ tools with 42 flags
- **8 Python modules** — orchestrator, tool catalog, workflows, sessions, enrichment, evidence, templates, interactive shell
- **Tool catalog** — 40 tools across 17 forensics categories with install detection
- **9 scan templates** — full-osint, quick-check, social-deep, email-verify, phone-trace, dark-web, corporate, relationship, dating-sweep
- **8 investigation workflows** — step-by-step guides with tool chaining
- **Plugin system** — drop `.py` files in `~/.recon/plugins/` to add custom tools
- **Session tracking** — named sessions with resume, multi-run history, finding aggregation
- **Chain of custody** — timestamped action logs, SHA-256 hashing, evidence bags
- **Exposure scoring** — 1-100 risk rating with category breakdown
- **Interactive shell** (`recon shell`) — REPL with history, auto-complete, session management
- **Learning engine** — `recon learn <tool>` with examples, `recon suggest` for next-step recommendations
- **Auto-update system** — weekly launchd job, `recon update` subcommand with `--pip`, `--brew`, `--bundled` flags
- **Portable installer** — `install.sh` with venv, PATH setup, prerequisite checks, verification
- **Uninstaller** — clean removal script
- **Relationship Investigation (SPOTLIGHT foundations)** — blackbird, cupidcr4wl, toutatis integration
- **OpSec controls** — VPN check, rate limiting, jitter, Tor routing, opsec warnings
- **Desktop notifications** — macOS notification on scan completion
- **Report export** — JSON, CSV, HTML, PDF, Markdown with auto-open

### Changed
- Rebranded from WhatsMyName CLI to Project RECON
- All color theme from cyan to blood-red (`#3a0000` → `#8b0000` → `#cc0000` → `#ff0000`)
- Entry point from `wmn` to `recon` (wmn still available for backward compatibility)

## [2.0.0] — 2025-02-25

### Added
- Python CLI (`wmn`) replacing shell scripts
- Async HTTP engine with configurable workers
- Multi-source data: WhatsMyName + Sherlock + Maigret (4,387+ sites)
- JSON, CSV, HTML export
- Category filtering, NSFW toggle
- Tor/proxy support

### Changed
- Complete rewrite from shell scripts to Python package
- Moved from manual checker scripts to `pip install -e .`

## [1.0.0] — 2023-05-01

### Added
- Initial WhatsMyName data file (`wmn-data.json`)
- Site detection format with `e_code`, `e_string`, `m_code`, `m_string`
- Community contribution workflow
- Creative Commons BY-SA 4.0 license

### Removed
- Legacy checker scripts (moved to community tools)
