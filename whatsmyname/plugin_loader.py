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
