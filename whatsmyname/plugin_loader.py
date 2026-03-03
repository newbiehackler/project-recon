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


def marketplace_install(plugin_name: str) -> dict:
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

    # Check if already installed
    ensure_plugin_dir()
    # Derive filename from download URL
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
