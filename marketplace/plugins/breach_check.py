"""
Breach Check — RECON Marketplace Plugin
Check if an email or username appears in known data breaches.

Install: recon plugins install breach-check
"""

RECON_TOOLS = [
    {
        "name": "breach-check",
        "command": "breach-check",
        "description": "Check emails/usernames against known data breach databases",
        "input_types": ["email", "username"],
        "passive": True,
        "args_template": ["{target}"],
        "category": "Email Investigation",
        "install_hint": "recon plugins install breach-check",
        "learn_more": "https://github.com/newbiehackler/project-recon",
        "examples": [
            {"desc": "Check an email for breaches", "cmd": "breach-check user@example.com"},
            {"desc": "Check a username", "cmd": "breach-check johndoe"},
        ],
        "works_well_with": [
            {"tool": "holehe", "reason": "Find which services an email is registered on"},
            {"tool": "h8mail", "reason": "Deep breach intelligence with API keys"},
        ],
    }
]

# ── Plugin implementation ────────────────────────────────────────

import json
import sys
import urllib.request
import urllib.error

# Public breach check APIs (no API key required)
BREACH_APIS = [
    {
        "name": "HaveIBeenPwned (proxy)",
        "url": "https://haveibeenpwned.com/unifiedsearch/{target}",
        "type": "email",
    },
    {
        "name": "BreachDirectory",
        "url": "https://breachdirectory.org/api/search?term={target}",
        "type": "both",
    },
]


def run(target: str, output_json: bool = False) -> dict:
    """Check a target against breach databases."""
    results = {
        "target": target,
        "breaches_found": 0,
        "sources_checked": len(BREACH_APIS),
        "details": [],
    }

    for api in BREACH_APIS:
        url = api["url"].format(target=target)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RECON/3.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    results["details"].append({
                        "source": api["name"],
                        "status": "found",
                        "note": "Target may appear in breach data",
                    })
                    results["breaches_found"] += 1
        except urllib.error.HTTPError as e:
            if e.code == 404:
                results["details"].append({
                    "source": api["name"],
                    "status": "clean",
                    "note": "Not found in this database",
                })
            else:
                results["details"].append({
                    "source": api["name"],
                    "status": "error",
                    "note": f"HTTP {e.code}",
                })
        except Exception as e:
            results["details"].append({
                "source": api["name"],
                "status": "error",
                "note": str(e)[:80],
            })

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n  Breach Check: {target}")
        print(f"  {'─' * 40}")
        for d in results["details"]:
            icon = "🔴" if d["status"] == "found" else "🟢" if d["status"] == "clean" else "⚠️"
            print(f"  {icon} {d['source']:25s}  {d['status']:8s}  {d['note']}")
        print(f"\n  {results['sources_checked']} sources checked, {results['breaches_found']} hits")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: breach-check <email_or_username> [--json]")
        sys.exit(1)

    target = sys.argv[1]
    output_json = "--json" in sys.argv
    run(target, output_json)


if __name__ == "__main__":
    main()
