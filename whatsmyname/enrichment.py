"""
RECON Enrichment Module — auto-enrich findings with additional intelligence.

Runs lightweight lookups on findings:
- Domain → whois registration, DNS records
- URL → extract domain, resolve IP, check HTTPS
- IP → reverse DNS, geolocation estimate
- Exposure scoring (1-100) based on findings
"""

from __future__ import annotations

import re
import shutil
import subprocess
from urllib.parse import urlparse


def _run_cmd(cmd: list[str], timeout: int = 10) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def extract_domain(url: str) -> str:
    """Extract domain from a URL."""
    try:
        parsed = urlparse(url)
        if parsed.hostname:
            return parsed.hostname
    except Exception:
        pass
    # Fallback: try to extract from string
    m = re.search(r"(?:https?://)?([^/\s:]+)", url)
    return m.group(1) if m else ""


def resolve_domain(domain: str) -> str | None:
    """Resolve a domain to IP using dig."""
    if not shutil.which("dig"):
        return None
    output = _run_cmd(["dig", "+short", domain])
    # Return first A record
    for line in output.splitlines():
        line = line.strip()
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", line):
            return line
    return None


def reverse_dns(ip: str) -> str | None:
    """Reverse DNS lookup."""
    if not shutil.which("dig"):
        return None
    output = _run_cmd(["dig", "+short", "-x", ip])
    return output.strip().rstrip(".") if output.strip() else None


def whois_summary(target: str) -> dict | None:
    """Get whois summary for a domain or IP."""
    if not shutil.which("whois"):
        return None
    output = _run_cmd(["whois", target], timeout=15)
    if not output:
        return None

    info = {}
    patterns = {
        "registrant": r"(?:Registrant|registrant).*?:\s*(.+)",
        "organization": r"(?:Org|Organization|org-name).*?:\s*(.+)",
        "created": r"(?:Creat|Registr).*?(?:Date|date).*?:\s*(.+)",
        "expires": r"(?:Expir|Registry Expiry).*?(?:Date|date).*?:\s*(.+)",
        "registrar": r"(?:Registrar)\s*:\s*(.+)",
        "country": r"(?:Country|country).*?:\s*(.+)",
        "nameservers": r"(?:Name Server|nserver).*?:\s*(.+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, output, re.IGNORECASE)
        if m:
            info[key] = m.group(1).strip()

    return info if info else None


def enrich_finding(finding: dict) -> dict:
    """
    Enrich a single finding with additional intelligence.
    Returns the finding dict with an 'enrichment' key added.
    """
    enrichment: dict = {}
    url = finding.get("url", "")

    if url and url.startswith("http"):
        domain = extract_domain(url)
        if domain:
            enrichment["domain"] = domain

            # Resolve to IP
            ip = resolve_domain(domain)
            if ip:
                enrichment["ip"] = ip
                # Reverse DNS
                rdns = reverse_dns(ip)
                if rdns:
                    enrichment["reverse_dns"] = rdns

    finding["enrichment"] = enrichment
    return finding


def enrich_findings(findings: list[dict], max_lookups: int = 20) -> list[dict]:
    """
    Enrich a list of findings. Limits DNS lookups to avoid flooding.
    """
    seen_domains: set[str] = set()
    lookup_count = 0
    enriched = []

    for f in findings:
        url = f.get("url", "")
        domain = extract_domain(url) if url else ""

        if domain and domain not in seen_domains and lookup_count < max_lookups:
            f = enrich_finding(f)
            seen_domains.add(domain)
            lookup_count += 1
        else:
            f["enrichment"] = {"domain": domain} if domain else {}

        enriched.append(f)

    return enriched


def calculate_exposure_score(findings: list[dict]) -> dict:
    """
    Calculate an exposure score (1-100) based on findings.

    Scoring factors:
    - Number of unique sites where target was found
    - Presence in breaches (high weight)
    - Number of categories
    - Registration on sensitive platforms
    """
    if not findings:
        return {"score": 0, "rating": "No Data", "breakdown": {}}

    unique_urls = set()
    categories = set()
    breach_count = 0
    social_count = 0
    sensitive_count = 0

    sensitive_sites = {
        "dating", "adult", "finance", "gambling", "crypto", "darknet",
    }

    for f in findings:
        if f.get("url"):
            unique_urls.add(f["url"].rstrip("/").lower())
        cat = f.get("category", "").lower()
        categories.add(cat)

        if "breach" in cat:
            breach_count += 1
        if "social" in cat:
            social_count += 1
        for s in sensitive_sites:
            if s in cat or s in f.get("site_name", "").lower():
                sensitive_count += 1

    # Calculate score components (each 0-20 points)
    presence_score = min(20, len(unique_urls) * 2)  # 10+ sites = max
    breach_score = min(25, breach_count * 8)  # Breaches are heavily weighted
    social_score = min(15, social_count * 3)
    category_score = min(15, len(categories) * 3)
    sensitive_score = min(25, sensitive_count * 10)

    total = min(100, presence_score + breach_score + social_score +
                category_score + sensitive_score)

    # Rating
    if total >= 80:
        rating = "CRITICAL"
    elif total >= 60:
        rating = "HIGH"
    elif total >= 40:
        rating = "MODERATE"
    elif total >= 20:
        rating = "LOW"
    else:
        rating = "MINIMAL"

    return {
        "score": total,
        "rating": rating,
        "breakdown": {
            "online_presence": presence_score,
            "data_breaches": breach_score,
            "social_media": social_score,
            "category_spread": category_score,
            "sensitive_platforms": sensitive_score,
        },
        "stats": {
            "unique_sites": len(unique_urls),
            "categories": len(categories),
            "breaches": breach_count,
        },
    }
