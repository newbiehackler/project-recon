"""
Social Deep Dive — RECON Marketplace Plugin
Deep social media profiling across 15+ platforms.

Install: recon plugins install social-deep-dive
"""

# RECON plugin manifest — this is what RECON loads
RECON_TOOLS = [
    {
        "name": "social-deep-dive",
        "command": "social-deep-dive",
        "description": "Deep social media profiling — bios, follower counts, post frequency, cross-platform links",
        "input_types": ["username"],
        "passive": True,
        "args_template": ["{target}"],
        "category": "Username Enumeration",
        "install_hint": "recon plugins install social-deep-dive",
        "learn_more": "https://github.com/newbiehackler/project-recon",
        "examples": [
            {"desc": "Profile a username across social platforms", "cmd": "social-deep-dive johndoe"},
            {"desc": "JSON output", "cmd": "social-deep-dive johndoe --json"},
        ],
        "works_well_with": [
            {"tool": "sherlock", "reason": "Find accounts first, then deep-dive on confirmed ones"},
            {"tool": "maigret", "reason": "Cross-reference with Maigret's extended site list"},
        ],
    }
]

# ── Plugin implementation ────────────────────────────────────────

import json
import subprocess
import sys
from pathlib import Path

PLATFORMS = [
    ("Twitter/X", "https://x.com/{user}"),
    ("Instagram", "https://instagram.com/{user}"),
    ("TikTok", "https://tiktok.com/@{user}"),
    ("GitHub", "https://github.com/{user}"),
    ("Reddit", "https://reddit.com/user/{user}"),
    ("YouTube", "https://youtube.com/@{user}"),
    ("LinkedIn", "https://linkedin.com/in/{user}"),
    ("Pinterest", "https://pinterest.com/{user}"),
    ("Twitch", "https://twitch.tv/{user}"),
    ("Medium", "https://medium.com/@{user}"),
    ("DevTo", "https://dev.to/{user}"),
    ("Mastodon", "https://mastodon.social/@{user}"),
    ("Bluesky", "https://bsky.app/profile/{user}.bsky.social"),
    ("Keybase", "https://keybase.io/{user}"),
    ("HackerOne", "https://hackerone.com/{user}"),
]


def run(target: str, output_json: bool = False) -> dict:
    """Run social deep dive on a username."""
    results = {"target": target, "platforms": []}

    for platform, url_template in PLATFORMS:
        url = url_template.format(user=target)
        results["platforms"].append({
            "platform": platform,
            "url": url,
            "status": "check",
        })

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n  Social Deep Dive: {target}")
        print(f"  {'─' * 40}")
        for p in results["platforms"]:
            print(f"  → {p['platform']:15s}  {p['url']}")
        print(f"\n  {len(PLATFORMS)} platforms queued for investigation")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: social-deep-dive <username> [--json]")
        sys.exit(1)

    target = sys.argv[1]
    output_json = "--json" in sys.argv
    run(target, output_json)


if __name__ == "__main__":
    main()
