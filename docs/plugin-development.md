# RECON Plugin Development Guide

Build and distribute your own OSINT plugins for Project RECON.

---

## Overview

RECON plugins are Python files that extend the tool arsenal. Drop a `.py` file in `~/.recon/plugins/` and RECON picks it up automatically — no config, no restart.

**Revenue model**: Plugins can be **free** or **paid** (70/30 split — you keep 70%, RECON project keeps 30%).

---

## Quick Start

```bash
# Scaffold a new plugin
recon plugins create my-scanner

# Edit the generated file
vim my-scanner.py

# Test it locally
cp my-scanner.py ~/.recon/plugins/
recon list-tools          # verify it shows up
recon johndoe --tools my-scanner   # run it

# Validate before submitting
recon plugins validate my-scanner.py

# Submit to the marketplace
recon plugins submit my-scanner.py
```

---

## Plugin File Structure

A plugin is a single `.py` file that defines a `RECON_TOOLS` list:

```python
"""
My Scanner — RECON Marketplace Plugin
Short description of what this plugin does.

Install: recon plugins install my-scanner
"""

RECON_TOOLS = [
    {
        "name": "my-scanner",                     # REQUIRED — unique tool name
        "command": "my-scanner",                   # REQUIRED — CLI binary name
        "description": "What this tool does",      # REQUIRED — shown in recon list-tools
        "input_types": ["username"],               # REQUIRED — username, email, and/or phone
        "args_template": ["{target}"],             # REQUIRED — how to pass the target
        "category": "Username Enumeration",        # optional — grouping in marketplace
        "passive": True,                           # optional — true = no direct interaction with target
        "install_hint": "pip install my-scanner",  # optional — how to install the binary
        "learn_more": "https://github.com/...",    # optional — project URL
        "examples": [                              # optional — usage examples
            {"desc": "Basic scan", "cmd": "my-scanner johndoe"},
            {"desc": "JSON output", "cmd": "my-scanner johndoe --json"},
        ],
        "works_well_with": [                       # optional — tool synergies
            {"tool": "sherlock", "reason": "Cross-reference results"},
        ],
    }
]
```

### Alternative: `register()` Function

For advanced plugins that need custom parsers:

```python
from whatsmyname.orchestrator import ToolConfig, InputType, Finding

def register() -> list[ToolConfig]:
    return [
        ToolConfig(
            name="my-scanner",
            command="my-scanner",
            description="What this tool does",
            input_types=[InputType.USERNAME],
            build_args=lambda target, tmpdir: [target],
            parse_output=my_parser,
            timeout=60,
        ),
    ]

def my_parser(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    findings = []
    for line in stdout.splitlines():
        if "http" in line:
            findings.append(Finding(
                source_tool="my-scanner",
                site_name="",
                url=line.strip(),
                category="custom",
            ))
    return findings
```

---

## Required Fields

Every tool in `RECON_TOOLS` **must** have:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique tool identifier (lowercase, hyphens) |
| `command` | string | CLI binary name (must be in PATH) |
| `description` | string | One-line description |
| `input_types` | list | One or more of: `"username"`, `"email"`, `"phone"` |
| `args_template` | list | CLI args with `{target}` placeholder |

---

## Validation Rules

Before submission, your plugin must pass `recon plugins validate`:

1. **Valid Python** — file compiles without syntax errors
2. **Defines tools** — has `RECON_TOOLS` list or `register()` function
3. **Required fields** — every tool entry has name, command, description, input_types
4. **No dangerous code** — no `eval()`, `exec()`, `os.system()`, or `subprocess` with `shell=True`
5. **Size limit** — file must be under 500 KB

---

## Testing Locally

```bash
# Copy your plugin to the plugins directory
cp my-scanner.py ~/.recon/plugins/

# Verify RECON loads it
recon list-tools
# Should show your tool with ✓ if the command binary exists, ✗ if not

# Test with a target
recon johndoe --tools my-scanner

# Remove when done testing
rm ~/.recon/plugins/my-scanner.py
```

---

## Submitting to the Marketplace

### Via CLI (Recommended)

```bash
recon plugins submit my-scanner.py
```

This validates your plugin and opens a GitHub Issue on the project repo with your plugin metadata. The maintainer will review and add it to the marketplace registry.

### Via GitHub (Manual)

1. Go to [github.com/newbiehackler/project-recon/issues/new](https://github.com/newbiehackler/project-recon/issues/new?template=plugin-submission.yml)
2. Select the **Plugin Submission** template
3. Fill in the details and attach your `.py` file
4. Submit the issue

### What Happens Next

1. Maintainer reviews the plugin for quality and security
2. Plugin is added to `marketplace/registry.json`
3. Plugin `.py` file is added to `marketplace/plugins/`
4. Users can install it: `recon plugins install my-scanner`

---

## Paid Plugins

Want to charge for your plugin? Set `tier: "paid"` in your submission.

### How It Works

1. You submit your plugin with a requested price (e.g., $10 one-time)
2. Maintainer creates a LemonSqueezy product page for the plugin
3. Plugin is listed as **PAID** in the marketplace with a purchase link
4. Users who buy receive a license key
5. Install with: `recon plugins install my-scanner --key RECON-MYSCN-abc123`

### Revenue Split

- **70%** goes to the plugin developer
- **30%** goes to the RECON project

Payouts are processed monthly via PayPal or bank transfer. Minimum payout threshold: $20.

### Pricing Guidelines

- Simple utilities: $5–$10
- Specialized tools: $10–$25
- Premium / multi-tool suites: $25–$50

---

## Best Practices

- **One plugin, one purpose** — don't bundle unrelated tools
- **Use `passive: True`** if your tool doesn't directly interact with the target
- **Include `install_hint`** so users know how to get the binary
- **Add `examples`** — they show up in tool documentation
- **Test with all your declared `input_types`** before submitting
- **Write a clear description** — it's the first thing users see in `recon plugins search`

---

## Example Plugins

Browse existing plugins for reference:

- [`social_deep_dive.py`](../marketplace/plugins/social_deep_dive.py) — social media profiling
- [`breach_check.py`](../marketplace/plugins/breach_check.py) — breach database queries
- [`geolocation_osint.py`](../marketplace/plugins/geolocation_osint.py) — geolocation extraction

---

## Questions?

Open an issue on [GitHub](https://github.com/newbiehackler/project-recon/issues) or check the [README](../README.md).
