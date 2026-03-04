#!/usr/bin/env python3
"""
OSINT Tools CLI — RECON Tool Reference Browser Wrapper

Launch the interactive TUI browser for 1,000+ OSINT tools and resources.
Built in Rust with ratatui for fast, keyboard-driven navigation.

Part of Project RECON — Rapid Evidence Collection & OSINT Network
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import textwrap
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
SRC_DIR = TOOL_DIR / "src"
BINARY = SRC_DIR / "target" / "release" / "osint-tools-cli"
VERSION = "1.0.0"

HELP_EPILOG = textwrap.dedent("""\

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     OSINT TOOLS CLI — Interactive OSINT Reference for RECON
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    OVERVIEW
    ────────
      Interactive terminal UI (TUI) for browsing 1,000+ OSINT tools and
      resources. Based on Cipher387's OSINT Stuff Tool Collection — the
      most comprehensive OSINT resource list on the internet.

      Navigate with keyboard only. No mouse needed. No browser needed.

    CATEGORIES
    ──────────
      Maps, Geolocation & Transport
        Social media maps, aviation, maritime, railway, routes,
        street view, satellite imagery, military tracking

      Social Media
        Twitter, YouTube, TikTok, Facebook, Instagram, LinkedIn,
        Reddit, Discord, Mastodon, Twitch, Snapchat, OnlyFans

      Domain/IP/Links
        Dorks, scrapers, subdomains, Cloudflare bypass, traffic,
        technology lookup, source code analysis

      Image Search & Identification
        Reverse image search, face recognition, EXIF analysis,
        font identification

      Cryptocurrencies, Messengers, Code, Search Engines, IOT,
      Archives, Passwords, Emails, Phone Numbers, and more.

    SUBCOMMANDS
    ───────────
      launch               Start the interactive TUI browser
      build                Build the Rust binary from source
      install-deps         Install Rust toolchain (if needed)

    EXAMPLES
    ────────
      # Launch the interactive browser
      osint-tools-cli launch

      # Build from source (first time)
      osint-tools-cli build

      # Install Rust toolchain
      osint-tools-cli install-deps

    KEYBOARD SHORTCUTS (in TUI)
    ───────────────────────────
      ↑/↓ or j/k      Navigate items
      Enter            Expand category / open tool
      Esc / q          Go back / quit
      /                Search
      Tab              Switch panels

    INVESTIGATION WORKFLOW
    ──────────────────────
      When you're stuck and need inspiration:
        1. Launch the browser:  osint-tools-cli launch
        2. Browse by category for your data type
        3. Find a new tool to try
        4. Use it with RECON:   recon learn <tool>

    WORKS WELL WITH
    ────────────────
      • recon learn      — Get beginner guides for tools found here
      • recon suggest    — RECON's own tool recommendation engine
      • recon categories — Browse RECON's integrated tool catalog

    REQUIREMENTS
    ────────────
      • Rust toolchain (install: curl --proto '=https' --tlsv1.2 -sSf
        https://sh.rustup.rs | sh)
      • Or pre-built binary (included if already compiled)

    VERSION
    ───────
      osint-tools-cli v1.0.0
      Part of Project RECON v3.0.0

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def cmd_launch(args: argparse.Namespace) -> int:
    if BINARY.exists():
        return subprocess.run([str(BINARY)]).returncode

    # Try cargo run as fallback
    cargo_toml = SRC_DIR / "Cargo.toml"
    if cargo_toml.exists():
        print("Binary not built yet. Building and running...")
        return subprocess.run(["cargo", "run", "--release"], cwd=str(SRC_DIR)).returncode

    print("✗ osint-tools-cli not built. Run: osint-tools-cli build")
    return 1


def cmd_build(args: argparse.Namespace) -> int:
    cargo_toml = SRC_DIR / "Cargo.toml"
    if not cargo_toml.exists():
        print("✗ Cargo.toml not found")
        return 1

    if not _has_cargo():
        print("✗ Rust toolchain not found. Run: osint-tools-cli install-deps")
        return 1

    print("Building osint-tools-cli (this may take a minute)...")
    result = subprocess.run(["cargo", "build", "--release"], cwd=str(SRC_DIR))
    if result.returncode == 0:
        print(f"✓ Built: {BINARY}")
    return result.returncode


def cmd_install_deps(args: argparse.Namespace) -> int:
    if _has_cargo():
        print("✓ Rust toolchain already installed")
        subprocess.run(["rustc", "--version"])
        return 0

    print("Installing Rust toolchain via rustup...")
    print("  This will install rustc, cargo, and rustup")
    result = subprocess.run(
        ["sh", "-c", "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"],
    )
    if result.returncode == 0:
        print("✓ Rust installed. Restart your shell or run: source ~/.cargo/env")
    return result.returncode


def _has_cargo() -> bool:
    try:
        return subprocess.run(["cargo", "--version"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="osint-tools-cli",
        description="OSINT Tools CLI — Interactive OSINT Reference for RECON",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"osint-tools-cli {VERSION}")

    sub = parser.add_subparsers(dest="command", title="subcommands")
    sub.add_parser("launch", help="Start the interactive TUI browser")
    sub.add_parser("build", help="Build the Rust binary from source")
    sub.add_parser("install-deps", help="Install Rust toolchain")

    args = parser.parse_args()
    handlers = {"launch": cmd_launch, "build": cmd_build, "install-deps": cmd_install_deps}

    if not args.command:
        # Default to launch
        args.command = "launch"

    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
