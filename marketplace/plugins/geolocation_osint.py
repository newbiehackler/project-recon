"""
Geolocation OSINT — RECON Marketplace Plugin
Extract and analyze geolocation data from digital footprints.

Install: recon plugins install geolocation-osint
"""

RECON_TOOLS = [
    {
        "name": "geo-osint",
        "command": "geo-osint",
        "description": "Extract geolocation data from photos, social posts, and IPs",
        "input_types": ["username"],
        "passive": True,
        "args_template": ["{target}"],
        "category": "Metadata Extraction",
        "install_hint": "recon plugins install geolocation-osint",
        "learn_more": "https://github.com/newbiehackler/project-recon",
        "examples": [
            {"desc": "Geolocate a username's digital footprint", "cmd": "geo-osint johndoe"},
            {"desc": "Check an IP address", "cmd": "geo-osint --ip 8.8.8.8"},
        ],
        "works_well_with": [
            {"tool": "exiftool", "reason": "Extract EXIF GPS data from downloaded photos"},
            {"tool": "theHarvester", "reason": "Find IPs associated with a target domain"},
        ],
    }
]

# ── Plugin implementation ────────────────────────────────────────

import json
import sys
import urllib.request
import urllib.error


def ip_lookup(ip: str) -> dict:
    """Geolocate an IP address using free API."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,as"
        req = urllib.request.Request(url, headers={"User-Agent": "RECON/3.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}


def username_geo_recon(target: str) -> dict:
    """Attempt geolocation intelligence gathering for a username."""
    results = {
        "target": target,
        "type": "username",
        "geo_hints": [],
        "recommendations": [
            "Run exiftool on any downloaded photos for EXIF GPS data",
            "Check social media posts for location tags and check-ins",
            "Look for timezone clues in post timestamps",
            "Search for the username on location-based platforms (Foursquare, Strava, etc.)",
        ],
    }

    # Check location-based platforms
    location_platforms = [
        ("Strava", f"https://www.strava.com/athletes/{target}"),
        ("Foursquare", f"https://foursquare.com/user/{target}"),
        ("Flickr", f"https://www.flickr.com/people/{target}"),
        ("Wikiloc", f"https://www.wikiloc.com/wikiloc/user.do?name={target}"),
        ("Geocaching", f"https://www.geocaching.com/p/default.aspx?u={target}"),
    ]

    for platform, url in location_platforms:
        results["geo_hints"].append({
            "platform": platform,
            "url": url,
            "note": "Location-rich platform — check for GPS tracks, check-ins, geotagged photos",
        })

    return results


def run(target: str, is_ip: bool = False, output_json: bool = False) -> dict:
    """Run geolocation OSINT."""
    if is_ip:
        results = ip_lookup(target)
    else:
        results = username_geo_recon(target)

    if output_json:
        print(json.dumps(results, indent=2))
    else:
        if is_ip:
            print(f"\n  Geolocation: {target}")
            print(f"  {'─' * 40}")
            if results.get("status") == "success":
                print(f"  Country:  {results.get('country', '?')}")
                print(f"  Region:   {results.get('regionName', '?')}")
                print(f"  City:     {results.get('city', '?')}")
                print(f"  Coords:   {results.get('lat', '?')}, {results.get('lon', '?')}")
                print(f"  ISP:      {results.get('isp', '?')}")
                print(f"  Org:      {results.get('org', '?')}")
            else:
                print(f"  Status: {results.get('status', 'unknown')}")
                print(f"  Message: {results.get('message', 'No data')}")
        else:
            print(f"\n  Geo OSINT: {target}")
            print(f"  {'─' * 40}")
            print(f"\n  Location-rich platforms to check:")
            for hint in results["geo_hints"]:
                print(f"  → {hint['platform']:15s}  {hint['url']}")
            print(f"\n  Recommendations:")
            for rec in results["recommendations"]:
                print(f"  • {rec}")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: geo-osint <username> [--ip] [--json]")
        sys.exit(1)

    target = sys.argv[1]
    is_ip = "--ip" in sys.argv
    output_json = "--json" in sys.argv
    run(target, is_ip, output_json)


if __name__ == "__main__":
    main()
