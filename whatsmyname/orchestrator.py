"""
OSINT Master Orchestrator
Triggers multiple OSINT tools in parallel from a single search query.
Supports username, email, and phone number inputs.
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import os
import re
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Input type detection
# ---------------------------------------------------------------------------

class InputType(Enum):
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"


def detect_input_type(value: str) -> InputType:
    """Auto-detect whether the input is a username, email, or phone number."""
    value = value.strip()
    if "@" in value and "." in value.split("@")[-1]:
        return InputType.EMAIL
    if re.match(r"^\+?\d[\d\s\-()]{6,}$", value):
        return InputType.PHONE
    return InputType.USERNAME


def parse_phone(value: str) -> tuple[str, str]:
    """Split a phone number into (country_code, number).
    Returns ('+1', '5551234567') style tuple.
    """
    digits = re.sub(r"[^\d+]", "", value)
    if digits.startswith("+"):
        # Try common country code lengths
        for length in (4, 3, 2):  # e.g. +1, +44, +380
            cc = digits[:length]
            num = digits[length:]
            if num:
                return cc, num
        return "+1", digits[1:]
    # No country code — assume US
    return "+1", digits


def email_variants(username: str) -> list[str]:
    """Generate common email variants from a username for email-based tools."""
    domains = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "protonmail.com", "icloud.com", "aol.com",
    ]
    return [f"{username}@{d}" for d in domains]


# ---------------------------------------------------------------------------
# Tool configuration
# ---------------------------------------------------------------------------

@dataclass
class ToolConfig:
    name: str
    command: str  # binary name
    description: str
    input_types: list[InputType]
    build_args: Any = None  # callable(input, tmpdir) -> list[str]
    parse_output: Any = None  # callable(stdout, stderr, tmpdir) -> list[Finding]
    timeout: int = 120
    enabled: bool = True


@dataclass
class Finding:
    source_tool: str
    site_name: str
    url: str
    category: str = "unknown"
    confidence: str = "found"
    extra: dict = field(default_factory=dict)


@dataclass
class ToolReport:
    tool_name: str
    status: str  # completed, failed, timeout, skipped, not_installed
    findings: list[Finding] = field(default_factory=list)
    raw_output: str = ""
    elapsed: float = 0.0
    error: str = ""


@dataclass
class UnifiedReport:
    target: str
    input_type: str
    timestamp: str
    tools_run: list[ToolReport] = field(default_factory=list)
    all_findings: list[Finding] = field(default_factory=list)

    @property
    def unique_urls(self) -> set[str]:
        return {f.url for f in self.all_findings if f.url}

    @property
    def found_count(self) -> int:
        return len(self.unique_urls)

    def by_category(self) -> dict[str, list[Finding]]:
        cats: dict[str, list[Finding]] = {}
        for f in self.all_findings:
            cats.setdefault(f.category, []).append(f)
        return dict(sorted(cats.items()))

    def by_tool(self) -> dict[str, list[Finding]]:
        tools: dict[str, list[Finding]] = {}
        for f in self.all_findings:
            tools.setdefault(f.source_tool, []).append(f)
        return dict(sorted(tools.items()))

    def deduplicated_findings(self) -> list[Finding]:
        seen: set[str] = set()
        deduped: list[Finding] = []
        for f in self.all_findings:
            key = f.url.rstrip("/").lower() if f.url else f"{f.source_tool}:{f.site_name}"
            if key not in seen:
                seen.add(key)
                deduped.append(f)
        return deduped


# ---------------------------------------------------------------------------
# Output parsers for each tool
# ---------------------------------------------------------------------------

def _parse_wmn(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse wmn JSON output."""
    findings = []
    json_files = list(Path(tmpdir).glob("*.json"))
    for jf in json_files:
        try:
            data = json.loads(jf.read_text())
            for r in data.get("results", []):
                findings.append(Finding(
                    source_tool="wmn",
                    site_name=r.get("site", ""),
                    url=r.get("url", ""),
                    category=r.get("category", "unknown"),
                ))
        except Exception:
            pass
    # Fallback: parse stdout for URLs
    if not findings:
        for line in stdout.splitlines():
            if "http" in line and "✓" in line:
                parts = line.split()
                for p in parts:
                    if p.startswith("http"):
                        findings.append(Finding(
                            source_tool="wmn", site_name="", url=p.strip(),
                        ))
    return findings


def _parse_sherlock(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse sherlock JSON output."""
    findings = []
    json_files = list(Path(tmpdir).glob("*.json"))
    for jf in json_files:
        try:
            data = json.loads(jf.read_text())
            for site, info in data.items():
                if isinstance(info, dict) and info.get("status", "").lower() == "claimed":
                    findings.append(Finding(
                        source_tool="sherlock",
                        site_name=site,
                        url=info.get("url_user", ""),
                        category="social",
                    ))
        except Exception:
            pass
    # Fallback: parse stdout
    if not findings:
        for line in stdout.splitlines():
            m = re.match(r"\[\+\]\s+(\S+):\s+(https?://\S+)", line)
            if m:
                findings.append(Finding(
                    source_tool="sherlock", site_name=m.group(1),
                    url=m.group(2), category="social",
                ))
    return findings


def _parse_maigret(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse maigret output."""
    findings = []
    # Check for JSON report files
    for jf in Path(tmpdir).rglob("*.json"):
        try:
            data = json.loads(jf.read_text())
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("url_user"):
                        findings.append(Finding(
                            source_tool="maigret",
                            site_name=item.get("sitename", item.get("name", "")),
                            url=item.get("url_user", ""),
                            category=",".join(item.get("tags", [])) or "social",
                        ))
            elif isinstance(data, dict):
                for site, info in data.items():
                    if isinstance(info, dict) and info.get("url_user"):
                        findings.append(Finding(
                            source_tool="maigret",
                            site_name=site,
                            url=info.get("url_user", ""),
                            category=",".join(info.get("tags", [])) or "social",
                        ))
        except Exception:
            pass
    # Fallback: parse stdout for [+] lines
    if not findings:
        for line in stdout.splitlines():
            m = re.search(r"\[\+\]\s+(\S+).*?(https?://\S+)", line)
            if not m:
                m = re.search(r"\[.*claimed.*\]\s+(\S+).*?(https?://\S+)", line, re.IGNORECASE)
            if m:
                findings.append(Finding(
                    source_tool="maigret", site_name=m.group(1),
                    url=m.group(2), category="social",
                ))
    return findings


def _parse_social_analyzer(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse social-analyzer JSON output."""
    findings = []
    try:
        # social-analyzer outputs JSON to stdout when --output json
        data = json.loads(stdout)
        items = data if isinstance(data, list) else data.get("detected", [])
        for item in items:
            if isinstance(item, dict):
                url = item.get("link", item.get("url", ""))
                if url:
                    findings.append(Finding(
                        source_tool="social-analyzer",
                        site_name=item.get("name", item.get("source", "")),
                        url=url,
                        category="social",
                        confidence=item.get("rate", "found"),
                    ))
    except json.JSONDecodeError:
        # Parse text output
        for line in stdout.splitlines():
            m = re.search(r"(https?://\S+)", line)
            if m and ("detected" in line.lower() or "found" in line.lower()):
                findings.append(Finding(
                    source_tool="social-analyzer", site_name="",
                    url=m.group(1), category="social",
                ))
    return findings


def _parse_socialscan(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse socialscan output."""
    findings = []
    # Check for JSON output
    for jf in Path(tmpdir).glob("*.txt"):
        try:
            data = json.loads(jf.read_text())
            for item in data:
                if isinstance(item, dict) and item.get("available") is False:
                    findings.append(Finding(
                        source_tool="socialscan",
                        site_name=item.get("platform", ""),
                        url=item.get("url", ""),
                        category="social",
                    ))
        except Exception:
            pass
    # Parse stdout
    if not findings:
        for line in stdout.splitlines():
            if "taken" in line.lower() or "unavailable" in line.lower():
                parts = line.split()
                site = parts[0] if parts else ""
                findings.append(Finding(
                    source_tool="socialscan",
                    site_name=site.strip(":"),
                    url="",
                    category="social",
                    confidence="taken",
                ))
    return findings


def _parse_nexfil(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse nexfil output."""
    findings = []
    for line in stdout.splitlines():
        m = re.search(r"\[\+\]\s*(https?://\S+)", line)
        if m:
            url = m.group(1).strip()
            # Try to extract site name from URL
            site = re.sub(r"https?://(www\.)?", "", url).split("/")[0]
            findings.append(Finding(
                source_tool="nexfil", site_name=site,
                url=url, category="social",
            ))
    return findings


def _parse_holehe(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse holehe output."""
    findings = []
    for line in stdout.splitlines():
        if "[+]" in line:
            # Format: [+] site.com
            m = re.search(r"\[\+\]\s+(\S+)", line)
            if m:
                site = m.group(1).strip()
                findings.append(Finding(
                    source_tool="holehe",
                    site_name=site,
                    url=f"https://{site}",
                    category="email-registered",
                    confidence="registered",
                ))
    return findings


def _parse_h8mail(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse h8mail output."""
    findings = []
    for line in stdout.splitlines():
        # h8mail shows breach data lines
        if "breach" in line.lower() or "leak" in line.lower() or "password" in line.lower():
            findings.append(Finding(
                source_tool="h8mail",
                site_name="breach-data",
                url="",
                category="breach",
                confidence="breach",
                extra={"raw": line.strip()},
            ))
        elif re.search(r"https?://", line):
            m = re.search(r"(https?://\S+)", line)
            if m:
                findings.append(Finding(
                    source_tool="h8mail",
                    site_name="breach-data",
                    url=m.group(1),
                    category="breach",
                ))
    return findings


def _parse_phoneinfoga(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse phoneinfoga output."""
    findings = []
    current_scanner = ""
    for line in stdout.splitlines():
        if "scanner:" in line.lower() or "running" in line.lower():
            m = re.search(r"(?:scanner|running)[:\s]+(\S+)", line, re.IGNORECASE)
            if m:
                current_scanner = m.group(1)
        if "valid" in line.lower() or "carrier" in line.lower() or "location" in line.lower():
            findings.append(Finding(
                source_tool="phoneinfoga",
                site_name=current_scanner or "phoneinfoga",
                url="",
                category="phone-intel",
                extra={"raw": line.strip()},
            ))
        m = re.search(r"(https?://\S+)", line)
        if m:
            findings.append(Finding(
                source_tool="phoneinfoga",
                site_name="phoneinfoga",
                url=m.group(1),
                category="phone-intel",
            ))
    # If we got nothing from parsing, capture raw output as a single finding
    if not findings and stdout.strip():
        findings.append(Finding(
            source_tool="phoneinfoga",
            site_name="phoneinfoga-raw",
            url="",
            category="phone-intel",
            extra={"raw": stdout.strip()[:2000]},
        ))
    return findings


def _parse_ignorant(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse ignorant output."""
    findings = []
    for line in stdout.splitlines():
        if "[+]" in line:
            m = re.search(r"\[\+\]\s+(\S+)", line)
            if m:
                site = m.group(1).strip()
                findings.append(Finding(
                    source_tool="ignorant",
                    site_name=site,
                    url=f"https://{site}",
                    category="phone-registered",
                    confidence="registered",
                ))
    return findings


def _parse_theharvester(stdout: str, stderr: str, tmpdir: str) -> list[Finding]:
    """Parse theHarvester output."""
    findings = []
    section = ""
    for line in stdout.splitlines():
        stripped = line.strip()
        if "emails" in stripped.lower() and "---" not in stripped:
            section = "emails"
        elif "hosts" in stripped.lower() and "---" not in stripped:
            section = "hosts"
        elif "urls" in stripped.lower() and "---" not in stripped:
            section = "urls"
        elif "---" in stripped:
            continue
        elif stripped and section:
            if section == "emails" and "@" in stripped:
                findings.append(Finding(
                    source_tool="theHarvester",
                    site_name="email",
                    url=f"mailto:{stripped}",
                    category="harvested-email",
                ))
            elif section == "urls" and "http" in stripped:
                findings.append(Finding(
                    source_tool="theHarvester",
                    site_name="url",
                    url=stripped,
                    category="harvested-url",
                ))
            elif section == "hosts":
                findings.append(Finding(
                    source_tool="theHarvester",
                    site_name="host",
                    url=stripped,
                    category="harvested-host",
                ))
    return findings


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

def _tool_available(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def build_tool_configs() -> list[ToolConfig]:
    """Build the list of all supported OSINT tools with their configurations."""

    tools = []

    # --- USERNAME TOOLS ---

    tools.append(ToolConfig(
        name="wmn",
        command="wmn",
        description="WhatsMyName – 4,387+ sites username enumeration",
        input_types=[InputType.USERNAME],
        build_args=lambda inp, td: [
            inp, "--output", "json", "--output-file",
            os.path.join(td, "wmn.json"), "--no-banner", "--no-color",
        ],
        parse_output=_parse_wmn,
        timeout=300,
    ))

    tools.append(ToolConfig(
        name="sherlock",
        command="sherlock",
        description="Sherlock – ~400 sites username search",
        input_types=[InputType.USERNAME],
        build_args=lambda inp, td: [
            inp, "--print-found", "--json",
            os.path.join(td, "sherlock.json"), "--timeout", "15",
        ],
        parse_output=_parse_sherlock,
        timeout=180,
    ))

    tools.append(ToolConfig(
        name="maigret",
        command="maigret",
        description="Maigret – ~3,000 sites deep username search",
        input_types=[InputType.USERNAME],
        build_args=lambda inp, td: [
            inp, "--timeout", "15", "-n", "100",
            "--folderoutput", td, "--no-progressbar",
            "-J", "simple",
        ],
        parse_output=_parse_maigret,
        timeout=300,
    ))

    tools.append(ToolConfig(
        name="social-analyzer",
        command="social-analyzer",
        description="Social Analyzer – 900+ sites profile detection",
        input_types=[InputType.USERNAME],
        build_args=lambda inp, td: [
            "--username", inp, "--mode", "fast",
            "--output", "json", "--filter", "good,maybe",
            "--method", "find",
        ],
        parse_output=_parse_social_analyzer,
        timeout=180,
    ))

    tools.append(ToolConfig(
        name="socialscan",
        command="socialscan",
        description="Socialscan – username/email availability on major platforms",
        input_types=[InputType.USERNAME, InputType.EMAIL],
        build_args=lambda inp, td: [
            inp, "--json", os.path.join(td, "socialscan.txt"),
        ],
        parse_output=_parse_socialscan,
        timeout=60,
    ))

    tools.append(ToolConfig(
        name="nexfil",
        command="nexfil",
        description="NExfil – OSINT username finder",
        input_types=[InputType.USERNAME],
        build_args=lambda inp, td: ["-u", inp, "-t", "15"],
        parse_output=_parse_nexfil,
        timeout=120,
    ))

    # --- EMAIL TOOLS ---

    tools.append(ToolConfig(
        name="holehe",
        command="holehe",
        description="Holehe – check which sites an email is registered on",
        input_types=[InputType.EMAIL],
        build_args=lambda inp, td: [inp, "--only-used", "--no-clear", "--no-color"],
        parse_output=_parse_holehe,
        timeout=120,
    ))

    tools.append(ToolConfig(
        name="h8mail",
        command="h8mail",
        description="h8mail – email breach data lookup",
        input_types=[InputType.EMAIL],
        build_args=lambda inp, td: ["-t", inp],
        parse_output=_parse_h8mail,
        timeout=90,
    ))

    # --- PHONE TOOLS ---

    tools.append(ToolConfig(
        name="phoneinfoga",
        command="phoneinfoga",
        description="PhoneInfoga – advanced phone number OSINT",
        input_types=[InputType.PHONE],
        build_args=lambda inp, td: ["scan", "-n", inp],
        parse_output=_parse_phoneinfoga,
        timeout=60,
    ))

    tools.append(ToolConfig(
        name="ignorant",
        command="ignorant",
        description="Ignorant – check phone registrations on social platforms",
        input_types=[InputType.PHONE],
        build_args=lambda inp, td: [
            *parse_phone(inp), "--only-used", "--no-color", "--no-clear",
        ],
        parse_output=_parse_ignorant,
        timeout=90,
    ))

    # --- GENERAL OSINT ---

    tools.append(ToolConfig(
        name="theHarvester",
        command="theharvester",
        description="theHarvester – gather emails, hosts, URLs from public sources",
        input_types=[InputType.USERNAME, InputType.EMAIL],
        build_args=lambda inp, td: [
            "-d", inp if "@" not in inp else inp.split("@")[0],
            "-b", "anubis,duckduckgo,rapiddns,hackertarget,urlscan",
            "-l", "100",
        ],
        parse_output=_parse_theharvester,
        timeout=120,
    ))

    # Filter to only tools that are actually installed
    for t in tools:
        t.enabled = _tool_available(t.command)

    # Load user plugins from ~/.recon/plugins/
    try:
        from whatsmyname.plugin_loader import load_all_plugins
        plugin_tools = load_all_plugins()
        for pt in plugin_tools:
            pt.enabled = _tool_available(pt.command)
            # Don't duplicate existing tools
            if not any(t.name.lower() == pt.name.lower() for t in tools):
                tools.append(pt)
    except Exception:
        pass  # Don't crash if plugin system fails

    return tools


# ---------------------------------------------------------------------------
# Async execution engine
# ---------------------------------------------------------------------------

async def _run_single_tool(
    tool: ToolConfig,
    raw_input: str,
    tmpdir: str,
    on_start: Any = None,
    on_finish: Any = None,
) -> ToolReport:
    """Run a single OSINT tool as a subprocess and parse its output."""

    if not tool.enabled:
        return ToolReport(
            tool_name=tool.name, status="not_installed",
            error=f"{tool.command} not found in PATH",
        )

    tool_tmpdir = os.path.join(tmpdir, tool.name)
    os.makedirs(tool_tmpdir, exist_ok=True)

    try:
        args = tool.build_args(raw_input, tool_tmpdir)
    except Exception as e:
        return ToolReport(tool_name=tool.name, status="failed", error=str(e))

    cmd = [tool.command] + [str(a) for a in args]

    if on_start:
        on_start(tool.name)

    t0 = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tool_tmpdir,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=tool.timeout,
        )
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        elapsed = time.monotonic() - t0

        findings = tool.parse_output(stdout, stderr, tool_tmpdir)

        report = ToolReport(
            tool_name=tool.name,
            status="completed",
            findings=findings,
            raw_output=stdout[:5000],
            elapsed=elapsed,
        )

    except asyncio.TimeoutError:
        elapsed = time.monotonic() - t0
        try:
            proc.kill()
        except Exception:
            pass
        report = ToolReport(
            tool_name=tool.name, status="timeout",
            elapsed=elapsed, error=f"Timed out after {tool.timeout}s",
        )

    except Exception as e:
        elapsed = time.monotonic() - t0
        report = ToolReport(
            tool_name=tool.name, status="failed",
            elapsed=elapsed, error=str(e),
        )

    if on_finish:
        on_finish(tool.name, report)

    return report


async def run_recon(
    target: str,
    input_type: InputType | None = None,
    tools_override: list[str] | None = None,
    email_expand: bool = True,
    timeout_override: int | None = None,
    on_start: Any = None,
    on_finish: Any = None,
) -> UnifiedReport:
    """
    Run all applicable OSINT tools against the target.

    Args:
        target: The username, email, or phone number to search.
        input_type: Override auto-detection.
        tools_override: Only run specific tools (by name).
        email_expand: For username searches, also generate email variants
                      and run email tools on them.
        timeout_override: Override individual tool timeouts.
        on_start: Callback(tool_name) when a tool starts.
        on_finish: Callback(tool_name, report) when a tool finishes.
    """

    if input_type is None:
        input_type = detect_input_type(target)

    all_tools = build_tool_configs()

    if timeout_override:
        for t in all_tools:
            t.timeout = timeout_override

    # Select tools applicable to this input type
    primary_tools = [
        t for t in all_tools
        if input_type in t.input_types
    ]

    # Apply tool name filter if specified
    if tools_override:
        override_lower = {n.lower() for n in tools_override}
        primary_tools = [t for t in primary_tools if t.name.lower() in override_lower]

    report = UnifiedReport(
        target=target,
        input_type=input_type.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    tmpdir = tempfile.mkdtemp(prefix="recon_")

    # Run primary tools in parallel
    tasks = [
        _run_single_tool(t, target, tmpdir, on_start, on_finish)
        for t in primary_tools
    ]

    # For username input, also run email tools on generated variants
    email_tasks = []
    if input_type == InputType.USERNAME and email_expand:
        email_tools = [t for t in all_tools if InputType.EMAIL in t.input_types]
        if tools_override:
            override_lower = {n.lower() for n in tools_override}
            email_tools = [t for t in email_tools if t.name.lower() in override_lower]

        variants = email_variants(target)
        for etool in email_tools:
            if not etool.enabled:
                continue
            for variant in variants:
                email_tasks.append(
                    _run_single_tool(etool, variant, tmpdir, on_start, on_finish)
                )

    all_results = await asyncio.gather(*tasks, *email_tasks, return_exceptions=True)

    for result in all_results:
        if isinstance(result, Exception):
            report.tools_run.append(ToolReport(
                tool_name="unknown", status="failed", error=str(result),
            ))
        else:
            report.tools_run.append(result)
            report.all_findings.extend(result.findings)

    # Clean up tmpdir
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass

    return report


# ---------------------------------------------------------------------------
# Report export
# ---------------------------------------------------------------------------

def export_json(report: UnifiedReport, path: str) -> None:
    deduped = report.deduplicated_findings()
    data = {
        "target": report.target,
        "input_type": report.input_type,
        "timestamp": report.timestamp,
        "summary": {
            "total_unique_accounts": len(deduped),
            "tools_completed": sum(1 for t in report.tools_run if t.status == "completed"),
            "tools_failed": sum(1 for t in report.tools_run if t.status in ("failed", "timeout")),
        },
        "tools": [
            {
                "name": t.tool_name,
                "status": t.status,
                "findings": len(t.findings),
                "elapsed": round(t.elapsed, 2),
                "error": t.error or None,
            }
            for t in report.tools_run
        ],
        "findings": [
            {
                "source": f.source_tool,
                "site": f.site_name,
                "url": f.url,
                "category": f.category,
                "confidence": f.confidence,
                **({"extra": f.extra} if f.extra else {}),
            }
            for f in deduped
        ],
    }
    Path(path).write_text(json.dumps(data, indent=2))


def export_csv(report: UnifiedReport, path: str) -> None:
    deduped = report.deduplicated_findings()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["source_tool", "site_name", "url", "category", "confidence"])
    for f in deduped:
        writer.writerow([f.source_tool, f.site_name, f.url, f.category, f.confidence])
    Path(path).write_text(buf.getvalue())


def export_html(report: UnifiedReport, path: str) -> None:
    deduped = report.deduplicated_findings()
    by_cat = {}
    for f in deduped:
        by_cat.setdefault(f.category, []).append(f)

    tool_rows = ""
    for t in report.tools_run:
        color = "#4caf50" if t.status == "completed" else "#f44336" if t.status in ("failed", "timeout") else "#ff9800"
        tool_rows += f'<tr><td>{t.tool_name}</td><td style="color:{color}">{t.status}</td><td>{len(t.findings)}</td><td>{t.elapsed:.1f}s</td></tr>\n'

    finding_rows = ""
    for cat in sorted(by_cat.keys()):
        for f in by_cat[cat]:
            link = f'<a href="{f.url}" target="_blank">{f.url}</a>' if f.url and f.url.startswith("http") else (f.url or "—")
            finding_rows += f"<tr><td>{f.source_tool}</td><td>{f.site_name}</td><td>{link}</td><td>{cat}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>RECON Report: {report.target}</title>
<style>
body {{ background:#1a1a2e; color:#e0e0e0; font-family:'Segoe UI',Tahoma,sans-serif; margin:2em; }}
h1 {{ color:#00d4ff; }} h2 {{ color:#7c4dff; border-bottom:1px solid #333; padding-bottom:6px; }}
.cards {{ display:flex; gap:1.5em; margin:1em 0; }}
.card {{ background:#16213e; border-radius:10px; padding:1.2em 2em; min-width:160px; text-align:center; }}
.card .num {{ font-size:2.2em; font-weight:700; color:#00d4ff; }}
.card .label {{ color:#999; font-size:0.9em; }}
table {{ width:100%; border-collapse:collapse; margin:1em 0; }}
th {{ background:#0f3460; padding:10px; text-align:left; }}
td {{ padding:8px 10px; border-bottom:1px solid #222; }}
tr:hover {{ background:#16213e; }}
a {{ color:#00d4ff; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
</style></head><body>
<h1>RECON Report</h1>
<p><strong>Target:</strong> {report.target} &nbsp;|&nbsp; <strong>Type:</strong> {report.input_type}
&nbsp;|&nbsp; <strong>Time:</strong> {report.timestamp}</p>
<div class="cards">
<div class="card"><div class="num">{len(deduped)}</div><div class="label">Unique Findings</div></div>
<div class="card"><div class="num">{sum(1 for t in report.tools_run if t.status=='completed')}</div><div class="label">Tools Completed</div></div>
<div class="card"><div class="num">{len(by_cat)}</div><div class="label">Categories</div></div>
</div>
<h2>Tool Results</h2>
<table><tr><th>Tool</th><th>Status</th><th>Findings</th><th>Time</th></tr>
{tool_rows}</table>
<h2>All Findings ({len(deduped)})</h2>
<table><tr><th>Source</th><th>Site</th><th>URL</th><th>Category</th></tr>
{finding_rows}</table>
</body></html>"""
    Path(path).write_text(html)
