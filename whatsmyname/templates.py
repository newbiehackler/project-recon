"""
RECON Scan Templates — predefined scan profiles for common investigation types.

Templates define which tools to run, timeout overrides, and behavior flags.
Usage: recon johndoe --template full-osint
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanTemplate:
    name: str
    description: str
    tools: list[str] | None = None  # None = all applicable
    passive_only: bool = False
    deep: bool = False
    quick: bool = False
    email_expand: bool = True
    timeout_multiplier: float = 1.0
    tags: list[str] = field(default_factory=list)


TEMPLATES: dict[str, ScanTemplate] = {
    "full-osint": ScanTemplate(
        name="full-osint",
        description="Maximum coverage — all tools, extended timeouts, email expansion",
        tools=None,  # All applicable
        deep=True,
        email_expand=True,
        timeout_multiplier=2.0,
        tags=["comprehensive", "slow"],
    ),
    "passive-only": ScanTemplate(
        name="passive-only",
        description="Non-intrusive only — no tools that touch the target directly",
        tools=["wmn", "sherlock", "maigret", "social-analyzer", "socialscan",
               "nexfil", "holehe", "h8mail", "ignorant", "theHarvester"],
        passive_only=True,
        email_expand=True,
        tags=["safe", "opsec"],
    ),
    "quick-check": ScanTemplate(
        name="quick-check",
        description="Fast 60-second scan — top 3 fastest tools only",
        tools=["wmn", "sherlock", "socialscan"],
        quick=True,
        email_expand=False,
        timeout_multiplier=0.5,
        tags=["fast", "lightweight"],
    ),
    "breach-check": ScanTemplate(
        name="breach-check",
        description="Focus on data breaches and email exposure",
        tools=["holehe", "h8mail", "socialscan"],
        email_expand=True,
        tags=["breach", "email", "focused"],
    ),
    "username-deep": ScanTemplate(
        name="username-deep",
        description="Deep username enumeration — all username tools, extended timeouts",
        tools=["wmn", "sherlock", "maigret", "social-analyzer", "socialscan", "nexfil"],
        deep=True,
        email_expand=False,
        timeout_multiplier=2.0,
        tags=["username", "comprehensive"],
    ),
    "phone-intel": ScanTemplate(
        name="phone-intel",
        description="Phone number investigation — carrier + platform registrations",
        tools=["phoneinfoga", "ignorant"],
        email_expand=False,
        tags=["phone", "focused"],
    ),
    "email-full": ScanTemplate(
        name="email-full",
        description="Complete email investigation — registrations + breaches + domain",
        tools=["holehe", "h8mail", "socialscan", "theHarvester"],
        email_expand=False,
        tags=["email", "comprehensive"],
    ),
    "relationship": ScanTemplate(
        name="relationship",
        description="SPOTLIGHT — full relationship investigation: dating sites + social + messaging + breaches",
        tools=["maigret", "blackbird", "cupidcr4wl", "holehe", "sherlock",
               "ignorant", "toutatis", "h8mail", "socialscan", "exiftool"],
        deep=True,
        email_expand=True,
        timeout_multiplier=2.0,
        tags=["spotlight", "relationship", "dating", "comprehensive"],
    ),
    "dating-sweep": ScanTemplate(
        name="dating-sweep",
        description="SPOTLIGHT Quick — fast dating/hookup platform check only",
        tools=["cupidcr4wl", "blackbird", "maigret"],
        quick=True,
        email_expand=False,
        timeout_multiplier=1.0,
        tags=["spotlight", "dating", "fast"],
    ),
}


def get_template(name: str) -> ScanTemplate | None:
    """Get a scan template by name."""
    return TEMPLATES.get(name.lower())


def list_templates() -> list[dict]:
    """List all available scan templates."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "tools": t.tools or ["all applicable"],
            "passive_only": t.passive_only,
            "deep": t.deep,
            "quick": t.quick,
            "tags": t.tags,
        }
        for t in TEMPLATES.values()
    ]
