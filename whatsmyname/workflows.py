"""
RECON Workflow Engine — suggests next steps after running tools.

Defines investigation workflows and chains tools together based on
findings and input types.
"""

from __future__ import annotations

from whatsmyname.tool_catalog import get_entry, get_suggestions_for

# ---------------------------------------------------------------------------
# Workflow definitions — common investigation patterns
# ---------------------------------------------------------------------------

WORKFLOWS: list[dict] = [
    {
        "name": "Full Username OSINT",
        "description": "Complete username investigation: enumerate profiles → check emails → search breaches",
        "steps": [
            {"tool": "wmn", "desc": "Enumerate username across 4,300+ sites"},
            {"tool": "sherlock", "desc": "Cross-validate with Sherlock's detection engine"},
            {"tool": "maigret", "desc": "Deep search with profile data extraction"},
            {"tool": "holehe", "desc": "Check email variants for service registrations"},
            {"tool": "h8mail", "desc": "Search email variants in breach databases"},
            {"tool": "exiftool", "desc": "Extract metadata from any discovered profile images"},
        ],
        "input_type": "username",
        "tags": ["osint", "username", "comprehensive"],
    },
    {
        "name": "Email Intelligence",
        "description": "Investigate an email address: registrations → breaches → domain analysis",
        "steps": [
            {"tool": "holehe", "desc": "Check which services the email is registered on"},
            {"tool": "h8mail", "desc": "Search for the email in data breaches"},
            {"tool": "socialscan", "desc": "Verify email availability on major platforms"},
            {"tool": "theharvester", "desc": "Find related emails and subdomains from the domain"},
            {"tool": "whois", "desc": "Whois the email's domain for registrant info"},
            {"tool": "dig", "desc": "Check DNS records (MX, SPF, DKIM) for the domain"},
        ],
        "input_type": "email",
        "tags": ["osint", "email", "comprehensive"],
    },
    {
        "name": "Phone Number Investigation",
        "description": "Full phone number analysis: carrier info → platform registrations",
        "steps": [
            {"tool": "phoneinfoga", "desc": "Get carrier, line type, and location data"},
            {"tool": "ignorant", "desc": "Check which platforms the number is registered on"},
            {"tool": "holehe", "desc": "If you find an associated email, check its registrations"},
            {"tool": "sherlock", "desc": "If you find a username, enumerate profiles"},
        ],
        "input_type": "phone",
        "tags": ["osint", "phone"],
    },
    {
        "name": "Network Reconnaissance",
        "description": "Full network analysis: discover hosts → scan services → capture traffic",
        "steps": [
            {"tool": "ping", "desc": "Verify target is alive"},
            {"tool": "traceroute", "desc": "Map the network path"},
            {"tool": "whois", "desc": "Look up IP/domain ownership"},
            {"tool": "dig", "desc": "Enumerate DNS records"},
            {"tool": "nmap", "desc": "Scan for open ports and services"},
            {"tool": "tshark", "desc": "Capture and analyze traffic"},
            {"tool": "curl", "desc": "Probe discovered web services"},
        ],
        "input_type": "ip",
        "tags": ["network", "scanning", "comprehensive"],
    },
    {
        "name": "Domain Investigation",
        "description": "Investigate a domain: DNS → ownership → subdomains → web analysis",
        "steps": [
            {"tool": "whois", "desc": "Look up domain registration and ownership"},
            {"tool": "dig", "desc": "Check all DNS record types (A, MX, TXT, NS, CNAME)"},
            {"tool": "theharvester", "desc": "Find emails, hosts, and subdomains"},
            {"tool": "nmap", "desc": "Scan the domain's IP for services"},
            {"tool": "curl", "desc": "Check HTTP headers and server technology"},
        ],
        "input_type": "domain",
        "tags": ["domain", "dns", "comprehensive"],
    },
    {
        "name": "File Forensics",
        "description": "Analyze a suspicious file: identify → metadata → hidden data → strings",
        "steps": [
            {"tool": "file", "desc": "Identify the real file type (don't trust the extension)"},
            {"tool": "exiftool", "desc": "Extract all metadata (GPS, author, dates, camera)"},
            {"tool": "strings", "desc": "Find readable text hidden in the file"},
            {"tool": "xxd", "desc": "Hex dump to inspect raw bytes"},
            {"tool": "steghide", "desc": "Check for steganography (JPEG/BMP/WAV only)"},
        ],
        "input_type": "file",
        "tags": ["forensics", "file", "analysis"],
    },
    {
        "name": "Passive OSINT Only",
        "description": "Non-intrusive investigation: only tools that don't touch the target",
        "steps": [
            {"tool": "wmn", "desc": "Username enumeration (passive web checks)"},
            {"tool": "sherlock", "desc": "Profile detection (passive web checks)"},
            {"tool": "holehe", "desc": "Email registration checks (passive login probes)"},
            {"tool": "whois", "desc": "Domain/IP registration data (public records)"},
            {"tool": "dig", "desc": "DNS lookups (public records)"},
            {"tool": "exiftool", "desc": "Metadata extraction (local file analysis)"},
        ],
        "input_type": "any",
        "tags": ["passive", "safe", "opsec"],
    },
    {
        "name": "Relationship Investigation (SPOTLIGHT)",
        "description": "Comprehensive infidelity/deception investigation: dating profiles → social media → communication apps → breaches → metadata",
        "steps": [
            {"tool": "maigret", "desc": "Deep username search with --tags dating to focus on dating/hookup sites"},
            {"tool": "blackbird", "desc": "600+ site sweep including dating platforms and forums"},
            {"tool": "cupidcr4wl", "desc": "Crawl adult content and dating platforms specifically"},
            {"tool": "holehe", "desc": "Check email registrations on dating services, social media, messaging apps"},
            {"tool": "sherlock", "desc": "Cross-validate with Sherlock's detection engine"},
            {"tool": "ignorant", "desc": "Check phone number registrations on WhatsApp, Telegram, Signal, etc."},
            {"tool": "toutatis", "desc": "Extract hidden emails/phone numbers from Instagram profile"},
            {"tool": "h8mail", "desc": "Search email in breach databases (leaked passwords reveal accounts)"},
            {"tool": "exiftool", "desc": "Check shared photos for GPS coordinates and timestamps"},
        ],
        "input_type": "username",
        "tags": ["relationship", "spotlight", "dating", "comprehensive"],
    },
]


# ---------------------------------------------------------------------------
# Suggestion engine
# ---------------------------------------------------------------------------

def get_workflows(input_type: str | None = None, tag: str | None = None) -> list[dict]:
    """Get applicable workflows, optionally filtered by input type or tag."""
    results = []
    for wf in WORKFLOWS:
        if input_type and wf["input_type"] not in (input_type, "any"):
            continue
        if tag and tag not in wf.get("tags", []):
            continue
        # Annotate steps with install status
        annotated_steps = []
        for step in wf["steps"]:
            entry = get_entry(step["tool"])
            annotated_steps.append({
                **step,
                "installed": entry.installed if entry else False,
            })
        results.append({**wf, "steps": annotated_steps})
    return results


def suggest_next_tools(
    current_tool: str,
    findings_categories: list[str] | None = None,
) -> list[dict]:
    """
    Suggest what tools to run next based on:
    1. The tool's 'works_well_with' list
    2. What categories of findings were produced
    3. What's actually installed
    """
    suggestions = get_suggestions_for(current_tool)

    # If we have findings, add context-aware suggestions
    if findings_categories:
        cats = set(findings_categories)
        extra = []

        if "social" in cats or "email-registered" in cats:
            for tool_name in ["h8mail", "holehe", "exiftool"]:
                if not any(s["tool"] == tool_name for s in suggestions):
                    entry = get_entry(tool_name)
                    if entry and entry.installed:
                        extra.append({
                            "tool": tool_name,
                            "reason": f"Found social/email results — {tool_name} can dig deeper",
                            "installed": True,
                            "install_hint": None,
                        })

        if "breach" in cats:
            for tool_name in ["sherlock", "maigret"]:
                if not any(s["tool"] == tool_name for s in suggestions):
                    entry = get_entry(tool_name)
                    if entry and entry.installed:
                        extra.append({
                            "tool": tool_name,
                            "reason": "Breaches found — check if leaked usernames have profiles",
                            "installed": True,
                            "install_hint": None,
                        })

        suggestions.extend(extra)

    return suggestions


def suggest_after_scan(
    input_type: str,
    tools_run: list[str],
    findings_categories: list[str],
) -> dict:
    """
    Generate post-scan suggestions including:
    - Tools from workflows that weren't run
    - Context-aware suggestions based on findings
    - Applicable workflows for next steps
    """
    # Find tools from applicable workflows that weren't run
    missed: list[dict] = []
    for wf in get_workflows(input_type=input_type):
        for step in wf["steps"]:
            if step["tool"] not in tools_run and step["installed"]:
                if not any(m["tool"] == step["tool"] for m in missed):
                    missed.append(step)

    # Get per-tool suggestions from what was run
    tool_suggestions: list[dict] = []
    for tool_name in tools_run:
        suggs = suggest_next_tools(tool_name, findings_categories)
        for s in suggs:
            if s["tool"] not in tools_run and s.get("installed"):
                if not any(ts["tool"] == s["tool"] for ts in tool_suggestions):
                    tool_suggestions.append(s)

    # Get relevant workflows
    relevant_workflows = get_workflows(input_type=input_type)

    return {
        "missed_tools": missed[:5],  # Top 5 most relevant
        "next_suggestions": tool_suggestions[:5],
        "workflows": relevant_workflows,
    }
