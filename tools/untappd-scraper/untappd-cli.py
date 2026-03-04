#!/usr/bin/env python3
"""
untappdScraper CLI — RECON Social Behavior Intelligence Wrapper

Scrapes Untappd.com user profiles for OSINT: drinking patterns, geolocation
data, friend networks, venue history, and behavioral analysis.

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
SCRIPT = TOOL_DIR / "untappd.py"
VERSION = "1.0.0"

BANNER = r"""
  ██╗   ██╗███╗   ██╗████████╗ █████╗ ██████╗ ██████╗ ██████╗
  ██║   ██║████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
  ██║   ██║██╔██╗ ██║   ██║   ███████║██████╔╝██████╔╝██║  ██║
  ██║   ██║██║╚██╗██║   ██║   ██╔══██║██╔═══╝ ██╔═══╝ ██║  ██║
  ╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║     ██║     ██████╔╝
   ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝
  Social Behavior Intelligence — RECON Module
"""

HELP_EPILOG = textwrap.dedent("""\

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     UNTAPPD SCRAPER — Social Behavior Intelligence for RECON
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    OVERVIEW
    ────────
      Scrapes public Untappd.com beer check-in profiles to extract OSINT:
        • Drinking patterns (time-of-day, day-of-week, binge detection)
        • Geographic locations (venues with GPS coordinates)
        • Friend/social network connections
        • Venue history with check-in counts
        • HTML heatmap of drinking locations

    WHAT YOU CAN LEARN
    ──────────────────
      From a single Untappd username you can determine:
        • Where someone lives and works (frequent venues)
        • Travel patterns (airport/hotel check-ins)
        • Daily schedule (when they drink → when they're free)
        • Social circle (who they drink with)
        • Behavioral patterns (binge drinking alerts)
        • Geographic heatmap of all activity

    EXAMPLES
    ────────
      # Full profile scrape
      untappd-scraper -u targetuser

      # Just recent check-in locations
      untappd-scraper -u targetuser --recent

      # Output includes:
      #   • User stats (total beers, badges, friends)
      #   • Friend list with names and locations
      #   • Drinking patterns by day-of-week
      #   • Drinking patterns by hour-of-day
      #   • Binge drinking alerts
      #   • Top venues with addresses and GPS
      #   • HTML heatmap file

    GEOCODING
    ─────────
      For GPS heatmap generation, you need a Google Geocoding API key:
        1. Get a key from https://developers.google.com/
        2. Edit geocode_api_keys.py:
             google_api_key = 'YOUR_KEY_HERE'

      The heatmap HTML file is written to the current directory.

    OUTPUT
    ──────
      • Terminal: Full text report with patterns and alerts
      • HTML file: Interactive heatmap of drinking locations
        (double-click to open in browser)

    INVESTIGATION WORKFLOW
    ──────────────────────
      1. Get username from social media or other OSINT
      2. Run scraper:           untappd-scraper -u targetuser
      3. Analyze patterns:      Look for work/home venue clusters
      4. Map friend network:    Cross-reference friends on other platforms
      5. Check-in metadata:     Correlate dates with other evidence
      6. Export for reporting:  Use the HTML heatmap in case files

    WORKS WELL WITH
    ────────────────
      • sherlock    — Find the Untappd username on other platforms
      • maigret     — Deep search across 3,000+ sites
      • holehe      — Check if associated emails are registered elsewhere
      • exiftool    — If they post photos, check for GPS metadata
      • blackbird   — Cross-reference on dating/social platforms

    PRIVACY NOTES
    ─────────────
      • Only scrapes PUBLIC profiles (private profiles are skipped)
      • No authentication required
      • Last 25 beers only (without API access)
      • Tip: Run weekly to build a rolling history over time

    REQUIREMENTS
    ────────────
      • Python 3.x
      • bs4, geocoder, gmplot, googlemaps, requests
      • Google Geocoding API key (optional, for heatmap)

    VERSION
    ───────
      untappd-scraper v1.0.0
      Part of Project RECON v3.0.0

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="untappd-scraper",
        description="untappdScraper — Social Behavior Intelligence for RECON",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"untappd-scraper {VERSION}")
    parser.add_argument("-u", "--user", required=True, help="Untappd username to investigate")
    parser.add_argument("-r", "--recent", action="store_true", help="Only dump recent check-in locations")

    args = parser.parse_args()

    if not SCRIPT.exists():
        print(f"✗ untappd.py not found at {SCRIPT}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, str(SCRIPT), "-u", args.user]
    if args.recent:
        cmd.append("-r")

    sys.exit(subprocess.run(cmd, cwd=str(TOOL_DIR)).returncode)


if __name__ == "__main__":
    main()
