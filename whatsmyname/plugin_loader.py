"""
RECON Plugin Loader — discover and load user plugins from ~/.recon/plugins/.

Each plugin file should define a `register()` function that returns a list
of ToolConfig objects (from whatsmyname.orchestrator).

Example plugin (~/.recon/plugins/my_tool.py):

    from whatsmyname.orchestrator import ToolConfig, InputType, Finding

    def register():
        return [ToolConfig(
            name="my_tool",
            command="my_tool",
            description="My custom OSINT tool",
            input_types=[InputType.USERNAME],
            build_args=lambda inp, td: [inp],
            parse_output=lambda out, err, td: [],
            timeout=60,
        )]
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path.home() / ".recon" / "plugins"


def ensure_plugin_dir() -> Path:
    """Create the plugin directory if it doesn't exist."""
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    return PLUGIN_DIR


def discover_plugins() -> list[Path]:
    """Find all .py plugin files in the plugin directory."""
    if not PLUGIN_DIR.exists():
        return []
    return sorted(
        p for p in PLUGIN_DIR.glob("*.py")
        if not p.name.startswith("_") and not p.name.endswith(".disabled")
    )


def load_plugin(path: Path) -> list[Any]:
    """
    Load a single plugin file and call its register() function.
    Returns a list of ToolConfig objects, or empty list on failure.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            f"recon_plugin_{path.stem}", str(path)
        )
        if spec is None or spec.loader is None:
            return []

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "register") and callable(module.register):
            result = module.register()
            if isinstance(result, list):
                return result
        return []

    except Exception as e:
        # Don't crash the whole app if a plugin is broken
        print(f"[!] Plugin error in {path.name}: {e}")
        return []


def load_all_plugins() -> list[Any]:
    """Load all plugins and return combined list of ToolConfig objects."""
    configs = []
    for plugin_path in discover_plugins():
        configs.extend(load_plugin(plugin_path))
    return configs


def list_plugins() -> list[dict]:
    """List all discovered plugins with their status."""
    plugins = []
    for path in discover_plugins():
        try:
            tools = load_plugin(path)
            plugins.append({
                "file": path.name,
                "path": str(path),
                "tools": [getattr(t, "name", "unknown") for t in tools],
                "status": "ok",
                "count": len(tools),
            })
        except Exception as e:
            plugins.append({
                "file": path.name,
                "path": str(path),
                "tools": [],
                "status": f"error: {e}",
                "count": 0,
            })
    return plugins


SAMPLE_PLUGIN = '''"""
Sample RECON Plugin — rename this file (remove .disabled) to activate.

Place plugin files in: ~/.recon/plugins/
Each plugin must define a register() function that returns a list of ToolConfig objects.
"""

from whatsmyname.orchestrator import ToolConfig, InputType, Finding
import re


def _parse_my_tool(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse output from your custom tool."""
    findings = []
    for line in stdout.splitlines():
        # Customize this parser for your tool's output format
        m = re.search(r"(https?://\\S+)", line)
        if m:
            findings.append(Finding(
                source_tool="my_tool",
                site_name="",
                url=m.group(1),
                category="custom",
            ))
    return findings


def register() -> list[ToolConfig]:
    """Return list of ToolConfig objects for this plugin."""
    return [
        ToolConfig(
            name="my_tool",
            command="my_tool",           # binary name in PATH
            description="Description of what your tool does",
            input_types=[InputType.USERNAME],  # USERNAME, EMAIL, or PHONE
            build_args=lambda inp, td: [inp],  # how to build CLI args
            parse_output=_parse_my_tool,       # output parser
            timeout=60,
        ),
    ]
'''


def install_sample_plugin() -> Path:
    """Install the sample plugin template."""
    ensure_plugin_dir()
    sample_path = PLUGIN_DIR / "_example.py.disabled"
    if not sample_path.exists():
        sample_path.write_text(SAMPLE_PLUGIN)
    return sample_path


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

REGISTRY_URL = "https://raw.githubusercontent.com/newbiehackler/project-recon/main/marketplace/registry.json"


def _ssl_context():
    """Build an SSL context — prefer certifi certs, fall back to defaults."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _fetch_registry() -> dict:
    """Fetch the plugin marketplace registry."""
    import json
    import urllib.request
    try:
        ctx = _ssl_context()
        req = urllib.request.Request(REGISTRY_URL, headers={"User-Agent": "RECON/3.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e), "plugins": []}


def marketplace_search(query: str | None = None) -> list[dict]:
    """Search the marketplace registry. Returns matching plugins."""
    registry = _fetch_registry()
    plugins = registry.get("plugins", [])
    if not query:
        return plugins
    q = query.lower()
    return [
        p for p in plugins
        if q in p["name"].lower()
        or q in p["description"].lower()
        or any(q in t.lower() for t in p.get("tags", []))
    ]


# ---------------------------------------------------------------------------
# Licenses
# ---------------------------------------------------------------------------

LICENSE_FILE = Path.home() / ".recon" / "licenses.json"


def _load_licenses() -> dict:
    """Load stored license keys."""
    import json
    if LICENSE_FILE.exists():
        try:
            return json.loads(LICENSE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_license(plugin_name: str, key: str) -> None:
    """Store a license key for a plugin."""
    import json
    licenses = _load_licenses()
    licenses[plugin_name.lower()] = key
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_FILE.write_text(json.dumps(licenses, indent=2))


def marketplace_install(plugin_name: str, license_key: str | None = None) -> dict:
    """Install a plugin from the marketplace by name."""
    import urllib.request
    registry = _fetch_registry()
    if registry.get("error"):
        return {"success": False, "error": f"Cannot reach registry: {registry['error']}"}

    # Find the plugin
    match = None
    for p in registry.get("plugins", []):
        if p["name"].lower() == plugin_name.lower():
            match = p
            break

    if not match:
        return {"success": False, "error": f"Plugin '{plugin_name}' not found in marketplace"}

    # --- Payment gating for paid plugins ---
    if match.get("tier") == "paid":
        # Check for stored license first
        stored = _load_licenses().get(plugin_name.lower())
        key = license_key or stored

        if not key:
            purchase_url = match.get("purchase_url", "")
            price = match.get("price", "?")
            return {
                "success": False,
                "needs_license": True,
                "error": f"This is a paid plugin (${price})",
                "purchase_url": purchase_url,
                "hint": f"recon plugins install {plugin_name} --key YOUR_LICENSE_KEY",
            }

        # Validate license key prefix
        expected_prefix = match.get("license_key_prefix", "")
        if expected_prefix and not key.startswith(expected_prefix):
            return {
                "success": False,
                "error": f"Invalid license key — expected key starting with '{expected_prefix}'",
            }

        # Store valid key for future use
        _save_license(plugin_name, key)

    # Check if already installed
    ensure_plugin_dir()
    filename = match["download_url"].split("/")[-1]
    dest = PLUGIN_DIR / filename

    if dest.exists():
        return {"success": False, "error": f"Already installed at {dest}"}

    # Download
    try:
        ctx = _ssl_context()
        req = urllib.request.Request(match["download_url"], headers={"User-Agent": "RECON/3.0"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            content = resp.read()
        dest.write_bytes(content)
        return {
            "success": True,
            "plugin": match["name"],
            "version": match["version"],
            "path": str(dest),
            "tools": match.get("tools_provided", []),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def marketplace_uninstall(plugin_name: str) -> dict:
    """Remove an installed marketplace plugin."""
    registry = _fetch_registry()
    match = None
    for p in registry.get("plugins", []):
        if p["name"].lower() == plugin_name.lower():
            match = p
            break

    if not match:
        return {"success": False, "error": f"Plugin '{plugin_name}' not found in registry"}

    filename = match["download_url"].split("/")[-1]
    dest = PLUGIN_DIR / filename

    if not dest.exists():
        return {"success": False, "error": f"Plugin not installed"}

    dest.unlink()
    return {"success": True, "plugin": plugin_name, "removed": str(dest)}


# ---------------------------------------------------------------------------
# Plugin Validation
# ---------------------------------------------------------------------------

REQUIRED_TOOL_FIELDS = {"name", "command", "description", "input_types"}
DANGEROUS_PATTERNS = [
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bos\.system\s*\(",
    r"subprocess.*shell\s*=\s*True",
    r"\b__import__\s*\(",
    r"\bcompile\s*\(",
]
MAX_PLUGIN_SIZE = 500 * 1024  # 500 KB


def validate_plugin(filepath: str) -> dict:
    """
    Validate a plugin file for marketplace submission.
    Returns {"valid": bool, "errors": [...], "warnings": [...], "metadata": {...}}.
    """
    import ast
    import re

    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict = {}
    path = Path(filepath)

    # --- File checks ---
    if not path.exists():
        return {"valid": False, "errors": [f"File not found: {filepath}"], "warnings": [], "metadata": {}}

    if not path.suffix == ".py":
        errors.append("File must be a .py file")

    size = path.stat().st_size
    if size > MAX_PLUGIN_SIZE:
        errors.append(f"File too large: {size:,} bytes (max {MAX_PLUGIN_SIZE:,})")
    elif size == 0:
        errors.append("File is empty")

    source = path.read_text(encoding="utf-8")

    # --- Syntax check ---
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return {"valid": False, "errors": errors, "warnings": warnings, "metadata": metadata}

    # --- Check for RECON_TOOLS or register() ---
    has_recon_tools = False
    has_register = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RECON_TOOLS":
                    has_recon_tools = True
        elif isinstance(node, ast.FunctionDef) and node.name == "register":
            has_register = True

    if not has_recon_tools and not has_register:
        errors.append("Plugin must define RECON_TOOLS list or register() function")

    # --- Dangerous code patterns ---
    for pattern in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, source)
        if matches:
            errors.append(f"Dangerous code detected: {pattern.split(chr(92))[-1].split('(')[0] if chr(92) in pattern else matches[0].strip()}")

    # --- Extract metadata from RECON_TOOLS if available ---
    if has_recon_tools:
        # Use ast.literal_eval on the RECON_TOOLS assignment node (safe, no exec)
        try:
            tools = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "RECON_TOOLS":
                            tools = ast.literal_eval(node.value)
                            break

            if not isinstance(tools, list) or len(tools) == 0:
                errors.append("RECON_TOOLS must be a non-empty list")
            else:
                for i, tool in enumerate(tools):
                    if not isinstance(tool, dict):
                        errors.append(f"RECON_TOOLS[{i}] must be a dict")
                        continue
                    missing = REQUIRED_TOOL_FIELDS - set(tool.keys())
                    if missing:
                        errors.append(f"RECON_TOOLS[{i}] missing required fields: {', '.join(sorted(missing))}")
                    if "args_template" not in tool:
                        warnings.append(f"RECON_TOOLS[{i}] missing args_template (recommended)")

                # Build metadata from first tool
                first = tools[0]
                metadata = {
                    "name": first.get("name", path.stem),
                    "description": first.get("description", ""),
                    "category": first.get("category", "General"),
                    "input_types": first.get("input_types", []),
                    "tools_provided": [t.get("name", "") for t in tools],
                    "tool_count": len(tools),
                }
        except Exception as e:
            # Can't safely extract — that's ok, just warn
            warnings.append(f"Could not extract RECON_TOOLS at parse time: {e}")

    if not metadata.get("name"):
        metadata["name"] = path.stem.replace("_", "-")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Plugin Scaffold
# ---------------------------------------------------------------------------

SCAFFOLD_TEMPLATE = '''"""\n{title} — RECON Marketplace Plugin\n{description}\n\nInstall: recon plugins install {name}\n"""\n\nRECON_TOOLS = [\n    {{\n        "name": "{name}",\n        "command": "{name}",\n        "description": "{description}",\n        "input_types": ["username"],\n        "args_template": ["{{target}}"],\n        "category": "General",\n        "passive": True,\n        "install_hint": "pip install {name}",\n        "learn_more": "",\n        "examples": [\n            {{"desc": "Basic scan", "cmd": "{name} johndoe"}},\n        ],\n        "works_well_with": [],\n    }}\n]\n\n\n# ── Plugin implementation ────────────────────────────────────────\n\nimport sys\nimport json\n\n\ndef run(target: str, output_json: bool = False) -> dict:\n    """Run {name} on a target."""\n    results = {{"target": target, "findings": []}}\n\n    # TODO: implement your tool logic here\n    # Example:\n    # results["findings"].append({{"url": f"https://example.com/{{target}}", "status": "found"}})\n\n    if output_json:\n        print(json.dumps(results, indent=2))\n    else:\n        print(f"\\n  {title}: {{target}}")\n        print(f"  {{\"─\" * 40}}")\n        for f in results["findings"]:\n            print(f"  → {{f}}")\n        if not results["findings"]:\n            print("  No findings yet — implement your logic above")\n\n    return results\n\n\ndef main():\n    if len(sys.argv) < 2:\n        print("Usage: {name} <target> [--json]")\n        sys.exit(1)\n    target = sys.argv[1]\n    output_json = "--json" in sys.argv\n    run(target, output_json)\n\n\nif __name__ == "__main__":\n    main()\n'''


def scaffold_plugin(name: str, output_dir: str = ".") -> dict:
    """Generate a new plugin scaffold file."""
    # Normalize name
    clean_name = name.lower().strip().replace(" ", "-")
    filename = clean_name.replace("-", "_") + ".py"
    title = clean_name.replace("-", " ").title()
    dest = Path(output_dir) / filename

    if dest.exists():
        return {"success": False, "error": f"File already exists: {dest}"}

    content = SCAFFOLD_TEMPLATE.format(
        name=clean_name,
        title=title,
        description=f"TODO: describe what {clean_name} does",
    )
    dest.write_text(content)
    return {"success": True, "path": str(dest), "name": clean_name}


# ---------------------------------------------------------------------------
# Plugin Submission
# ---------------------------------------------------------------------------

SUBMIT_REPO = "newbiehackler/project-recon"


def marketplace_submit(filepath: str, tier: str = "free", price: float = 0) -> dict:
    """
    Submit a plugin to the marketplace via GitHub Issue.
    Requires the `gh` CLI to be installed and authenticated.
    """
    import shutil
    import subprocess

    # Check gh CLI
    if not shutil.which("gh"):
        return {"success": False, "error": "GitHub CLI (gh) not found. Install: brew install gh"}

    # Validate first
    result = validate_plugin(filepath)
    if not result["valid"]:
        return {
            "success": False,
            "error": "Plugin validation failed",
            "validation_errors": result["errors"],
        }

    meta = result["metadata"]
    path = Path(filepath)
    source = path.read_text(encoding="utf-8")

    # Truncate source for issue body if very long
    source_preview = source[:4000]
    if len(source) > 4000:
        source_preview += f"\n\n... (truncated, full file: {len(source):,} bytes)"

    tier_label = f"${price}" if tier == "paid" and price > 0 else "FREE"
    warnings_text = ""
    if result["warnings"]:
        warnings_text = "\n### Warnings\n" + "\n".join(f"- ⚠️ {w}" for w in result["warnings"])

    issue_title = f"[Plugin Submission] {meta.get('name', path.stem)}"
    issue_body = f"""## Plugin Submission

| Field | Value |
|-------|-------|
| **Name** | {meta.get('name', path.stem)} |
| **Author** | (submitter) |
| **Category** | {meta.get('category', 'General')} |
| **Input Types** | {', '.join(meta.get('input_types', []))} |
| **Tools Provided** | {', '.join(meta.get('tools_provided', []))} |
| **Tier** | {tier_label} |
| **Description** | {meta.get('description', 'N/A')} |

### Validation
✅ Passed all checks{warnings_text}

### Source Code
```python
{source_preview}
```

---
*Submitted via `recon plugins submit`*
"""

    try:
        proc = subprocess.run(
            [
                "gh", "issue", "create",
                "--repo", SUBMIT_REPO,
                "--title", issue_title,
                "--body", issue_body,
                "--label", "plugin-submission",
            ],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode == 0:
            issue_url = proc.stdout.strip()
            return {"success": True, "issue_url": issue_url, "plugin": meta.get("name", path.stem)}
        else:
            # Label might not exist — retry without it
            proc2 = subprocess.run(
                [
                    "gh", "issue", "create",
                    "--repo", SUBMIT_REPO,
                    "--title", issue_title,
                    "--body", issue_body,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if proc2.returncode == 0:
                issue_url = proc2.stdout.strip()
                return {"success": True, "issue_url": issue_url, "plugin": meta.get("name", path.stem)}
            return {"success": False, "error": proc2.stderr.strip() or "Failed to create GitHub issue"}
    except FileNotFoundError:
        return {"success": False, "error": "GitHub CLI (gh) not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}
