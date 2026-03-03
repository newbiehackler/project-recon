"""
RECON CLI — One search, every OSINT tool.
Entry point for the unified OSINT orchestrator.

Subcommands:
  recon <target>        Search a username/email/phone across all tools
  recon inventory       Show all forensics tools and install status
  recon learn <tool>    Beginner-friendly guide with examples
  recon suggest <tool>  What to run next and why
  recon categories      Browse tools by category
  recon workflows       Show investigation workflow templates
  recon templates       List predefined scan profiles
  recon plugins         List loaded plugins
  recon shell           Interactive investigation REPL
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from threading import Lock

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns

from whatsmyname.orchestrator import (
    InputType,
    ToolReport,
    UnifiedReport,
    build_tool_configs,
    detect_input_type,
    export_csv,
    export_html,
    export_json,
    run_recon,
)

BANNER = r"""
[bold #ff0000]  ┏[/bold #ff0000][#0d0d0d]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/#0d0d0d][bold #ff0000]┓[/bold #ff0000]
[bold #ff0000]  ┃[/bold #ff0000][#1a1a1a] ░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ [/#1a1a1a][bold #ff0000]┃[/bold #ff0000]
[#0d0d0d]  ┃[/#0d0d0d][bold #330000]   ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗[/bold #330000]   [#0d0d0d]┃[/#0d0d0d]
[#0d0d0d]  ┃[/#0d0d0d][bold #770000]   ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║[/bold #770000]   [#0d0d0d]┃[/#0d0d0d]
[#0d0d0d]  ┃[/#0d0d0d][bold #ff0000]   ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║[/bold #ff0000]   [#0d0d0d]┃[/#0d0d0d]
[#0d0d0d]  ┃[/#0d0d0d][bold #770000]   ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║[/bold #770000]   [#0d0d0d]┃[/#0d0d0d]
[#0d0d0d]  ┃[/#0d0d0d][bold #330000]   ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║[/bold #330000]   [#0d0d0d]┃[/#0d0d0d]
[#0d0d0d]  ┃[/#0d0d0d][#1a0000]   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝[/#1a0000]   [#0d0d0d]┃[/#0d0d0d]
[bold #ff0000]  ┃[/bold #ff0000][#1a1a1a] ░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ [/#1a1a1a][bold #ff0000]┃[/bold #ff0000]
[bold #ff0000]  ┗[/bold #ff0000][#0d0d0d]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/#0d0d0d][bold #ff0000]┛[/bold #ff0000]
[#1a1a1a]  ┣━[/#1a1a1a] [bold #ff0000]▐█[/bold #ff0000] [bold #ff0000]R[/bold #ff0000][#555555]apid[/#555555] [bold #ff0000]E[/bold #ff0000][#555555]vidence[/#555555] [bold #ff0000]C[/bold #ff0000][#555555]ollection[/#555555] [bold #ff0000]&[/bold #ff0000] [bold #ff0000]O[/bold #ff0000][#555555]SINT[/#555555] [bold #ff0000]N[/bold #ff0000][#555555]etwork[/#555555]
[#1a1a1a]  ┣━[/#1a1a1a] [bold #ff0000 on #0d0d0d] ☠ PROJECT RECON ☠ [/bold #ff0000 on #0d0d0d] [bold #ff0000]v3.0.0[/bold #ff0000]
[#1a1a1a]  ┗━[/#1a1a1a] [#0d0d0d]█▓▒░[/#0d0d0d][bold #ff0000] ARMED [/bold #ff0000][#0d0d0d]░▒▓█[/#0d0d0d] [#333333]// One Search · Every Tool · No Mercy //[/#333333]
"""

console = Console()


# ---------------------------------------------------------------------------
# Status display helpers
# ---------------------------------------------------------------------------

def _build_status_table(
    tool_states: dict[str, str],
    tool_findings: dict[str, int],
    tool_elapsed: dict[str, float],
) -> Table:
    table = Table(title="Tool Status", expand=True, border_style="dim")
    table.add_column("Tool", style="red", min_width=18)
    table.add_column("Status", min_width=14)
    table.add_column("Findings", justify="right", min_width=10)
    table.add_column("Time", justify="right", min_width=8)

    status_styles = {
        "waiting": "[dim]⏳ waiting[/dim]",
        "running": "[yellow]⚡ running[/yellow]",
        "completed": "[green]✓ completed[/green]",
        "failed": "[red]✗ failed[/red]",
        "timeout": "[red]⏱ timeout[/red]",
        "not_installed": "[dim]— skipped[/dim]",
    }

    for tool_name in sorted(tool_states.keys()):
        status_val = tool_states[tool_name]
        styled = status_styles.get(status_val, status_val)
        findings = str(tool_findings.get(tool_name, "—"))
        elapsed = f"{tool_elapsed.get(tool_name, 0):.1f}s" if tool_name in tool_elapsed else "—"
        table.add_row(tool_name, styled, findings, elapsed)

    return table


def _print_results(report: UnifiedReport) -> None:
    deduped = report.deduplicated_findings()
    cards = []
    cards.append(Panel(
        f"[bold red]{len(deduped)}[/bold red]\n[dim]Unique Findings[/dim]",
        width=22, border_style="red",
    ))
    completed = sum(1 for t in report.tools_run if t.status == "completed")
    total = sum(1 for t in report.tools_run if t.status != "not_installed")
    cards.append(Panel(
        f"[bold green]{completed}[/bold green][dim]/{total}[/dim]\n[dim]Tools Completed[/dim]",
        width=22, border_style="green",
    ))
    by_cat = report.by_category()
    cards.append(Panel(
        f"[bold magenta]{len(by_cat)}[/bold magenta]\n[dim]Categories[/dim]",
        width=22, border_style="magenta",
    ))
    console.print()
    console.print(Columns(cards, padding=(0, 2)))
    console.print()

    if not deduped:
        console.print("[yellow]No findings across any tool.[/yellow]")
        return

    console.print("[bold]Tool Breakdown[/bold]")
    tool_table = Table(border_style="dim", expand=True)
    tool_table.add_column("Tool", style="red")
    tool_table.add_column("Status")
    tool_table.add_column("Findings", justify="right")
    tool_table.add_column("Time", justify="right")
    tool_table.add_column("Error", style="dim red", max_width=40)

    for t in sorted(report.tools_run, key=lambda x: x.tool_name):
        if t.status == "not_installed":
            continue
        color = "green" if t.status == "completed" else "red"
        tool_table.add_row(
            t.tool_name,
            f"[{color}]{t.status}[/{color}]",
            str(len(t.findings)),
            f"{t.elapsed:.1f}s",
            t.error[:40] if t.error else "",
        )
    console.print(tool_table)
    console.print()

    console.print("[bold]Findings by Category[/bold]")
    for cat in sorted(by_cat.keys()):
        findings = by_cat[cat]
        console.print(f"\n  [bold magenta]{cat}[/bold magenta] ({len(findings)})")
        for f in findings:
            src = f"[dim]{f.source_tool}[/dim]"
            if f.url and f.url.startswith("http"):
                console.print(f"    [green]✓[/green] {f.site_name or f.url}  {src}")
                console.print(f"      [red]{f.url}[/red]")
            elif f.url:
                console.print(f"    [green]✓[/green] {f.site_name}: {f.url}  {src}")
            elif f.extra.get("raw"):
                console.print(f"    [yellow]ℹ[/yellow] {f.site_name}  {src}")
                raw_preview = f.extra["raw"][:120]
                console.print(f"      [dim]{raw_preview}[/dim]")
            else:
                console.print(f"    [green]✓[/green] {f.site_name}  {src}")


# ---------------------------------------------------------------------------
# Dynamic epilog generation
# ---------------------------------------------------------------------------

def _build_dynamic_epilog() -> str:
    """Generate help epilog from actual installed tools."""
    tools = build_tool_configs()
    by_type: dict[str, list[str]] = {"Username": [], "Email": [], "Phone": []}
    type_map = {InputType.USERNAME: "Username", InputType.EMAIL: "Email", InputType.PHONE: "Phone"}

    for t in tools:
        if t.enabled:
            for it in t.input_types:
                label = type_map.get(it)
                if label and t.name not in by_type[label]:
                    by_type[label].append(t.name)

    lines = [
        "",
        "Input auto-detection:",
        "  username    alphanumeric string (e.g. johndoe)",
        "  email       contains @ (e.g. johndoe@gmail.com)",
        "  phone       starts with + or is all digits (e.g. +15551234567)",
        "",
        "Installed tools:",
    ]
    for label, tool_names in by_type.items():
        if tool_names:
            lines.append(f"  {label + ':':10s} {', '.join(tool_names)}")

    lines.extend([
        "",
        "Subcommands:",
        "  recon inventory              Scan system for all forensics tools",
        "  recon learn <tool>           Beginner-friendly tool guide",
        "  recon suggest <tool>         What to run next and why",
        "  recon categories             Browse tools by category",
        "  recon workflows              Investigation workflow templates",
        "  recon templates              Predefined scan profiles",
        "  recon plugins                List loaded plugins",
        "  recon update                 Update all tools & dependencies",
        "  recon shell                  Interactive investigation REPL",
        "",
        "Examples:",
        "  recon johndoe                          # username search across all tools",
        "  recon johndoe@gmail.com                # email search",
        "  recon +15551234567                     # phone search",
        "  recon johndoe --tools wmn,sherlock     # only specific tools",
        "  recon johndoe --template quick-check   # use predefined scan profile",
        "  recon johndoe --deep --discover        # deep scan with suggestions",
        "  recon johndoe --dry-run                # show what would run",
        "  recon johndoe --session case001        # track in a session",
        "  recon learn nmap                       # learn about nmap",
        "  recon suggest sherlock                 # what to run after sherlock",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="recon",
        description="Project RECON — Rapid Evidence Collection & OSINT Network.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_build_dynamic_epilog(),
    )

    p.add_argument("target", nargs="?", default=None, help="Username, email, or phone number to search")
    p.add_argument("--type", choices=["username", "email", "phone"], help="Override auto-detection of input type")
    p.add_argument("--tools", type=str, default=None, help="Comma-separated list of tools to run (default: all applicable)")
    p.add_argument("--no-email-expand", action="store_true", help="Don't generate email variants for username searches")
    p.add_argument("--timeout", type=int, default=None, help="Override per-tool timeout in seconds")
    p.add_argument("-o", "--output", choices=["json", "csv", "html"], help="Export unified report")
    p.add_argument("--output-file", type=str, default=None, help="Custom output file path")
    p.add_argument("--no-banner", action="store_true", help="Skip the ASCII banner")
    p.add_argument("--list-tools", action="store_true", help="List all supported tools and their install status")
    p.add_argument("-V", "--version", action="version", version="Project RECON 3.0.0 — Rapid Evidence Collection & OSINT Network")

    # --- Scan control ---
    scan = p.add_argument_group("Scan control")
    scan.add_argument("--deep", action="store_true", help="All tools, 2x timeouts (comprehensive)")
    scan.add_argument("--quick", action="store_true", help="Top 3 fastest tools only")
    scan.add_argument("--passive", action="store_true", help="Only passive/non-intrusive tools")
    scan.add_argument("--proxy", type=str, default=None, help="Route tool traffic through proxy URL")
    scan.add_argument("--tor", action="store_true", help="Route through Tor (socks5://127.0.0.1:9050)")
    scan.add_argument("--parallel", type=int, default=None, help="Limit tool concurrency (default: unlimited)")
    scan.add_argument("--retries", type=int, default=0, help="Retry failed/timed-out tools N times")
    scan.add_argument("--dry-run", action="store_true", help="Show what would run without executing")
    scan.add_argument("--template", type=str, default=None, help="Use predefined scan profile (e.g. full-osint, quick-check)")

    # --- Input ---
    inp = p.add_argument_group("Input")
    inp.add_argument("-f", "--file", type=str, default=None, help="Read targets from file (one per line)")
    inp.add_argument("--stdin", action="store_true", help="Read targets from stdin")

    # --- Output ---
    out = p.add_argument_group("Output")
    out.add_argument("--raw", action="store_true", help="Show raw stdout from each tool")
    out.add_argument("--save-raw", type=str, default=None, help="Save raw tool outputs to directory")
    out.add_argument("--no-color", action="store_true", help="Plain text output (no colors)")
    out.add_argument("--open", action="store_true", help="Auto-open HTML report in browser")
    out.add_argument("--pdf", action="store_true", help="Export as PDF (requires html output)")
    out.add_argument("--markdown", action="store_true", help="Export as Markdown")

    # --- Investigation ---
    inv = p.add_argument_group("Investigation")
    inv.add_argument("--session", type=str, default=None, help="Track in named session (creates/resumes)")
    inv.add_argument("--case-id", type=str, default=None, help="Tag report with case ID")
    inv.add_argument("--notes", type=str, default=None, help="Attach investigator notes")
    inv.add_argument("--examiner", type=str, default=None, help="Tag who ran the investigation")
    inv.add_argument("--discover", action="store_true", help="Auto-suggest complementary tools after scan")
    inv.add_argument("--enrich", action="store_true", help="Auto-enrich findings (DNS, whois)")
    inv.add_argument("--score", action="store_true", help="Calculate exposure risk score (1-100)")
    inv.add_argument("--correlate", action="store_true", help="Cross-reference findings across tools")
    inv.add_argument("--diff", type=str, default=None, help="Compare against a previous scan JSON")

    # --- Chain of custody ---
    coc = p.add_argument_group("Chain of custody")
    coc.add_argument("--evidence-bag", type=str, default=None, help="Save to forensically sound evidence bag directory")
    coc.add_argument("--chain-of-custody", action="store_true", help="Log all actions with timestamps")
    coc.add_argument("--hash-verify", action="store_true", help="SHA-256 hash all outputs")

    # --- OpSec ---
    opsec = p.add_argument_group("OpSec")
    opsec.add_argument("--opsec-check", action="store_true", help="Warn about tools that leave traces")
    opsec.add_argument("--vpn-check", action="store_true", help="Refuse to run if VPN not detected")
    opsec.add_argument("--rate-limit", type=int, default=None, help="Global requests/second cap")
    opsec.add_argument("--jitter", action="store_true", help="Random delays between tool launches")

    # --- Automation ---
    auto = p.add_argument_group("Automation")
    auto.add_argument("--webhook", type=str, default=None, help="POST results to URL when complete")
    auto.add_argument("--notify", action="store_true", help="Desktop notification when done")
    auto.add_argument("--on-finding", type=str, default=None, help="Execute command for each finding")
    auto.add_argument("--filter", type=str, default=None, help="Filter results (e.g. category=social)")

    # --- Learning ---
    learn = p.add_argument_group("Learning")
    learn.add_argument("--cheatsheet", type=str, default=None, metavar="TOOL", help="Quick reference card for a tool")
    learn.add_argument("--explain", type=str, default=None, metavar="TERM", help="Explain a forensics concept")

    return p.parse_args(argv)


# ---------------------------------------------------------------------------
# Subcommand: inventory
# ---------------------------------------------------------------------------

def cmd_inventory() -> None:
    """Scan system for ALL known forensics/OSINT tools."""
    from whatsmyname.tool_catalog import get_by_category

    cats = get_by_category()
    installed_count = 0
    total_count = 0

    for cat_name in sorted(cats.keys()):
        entries = cats[cat_name]
        console.print(f"\n  [bold magenta]{cat_name}[/bold magenta]")

        for entry in entries:
            total_count += 1
            if entry.installed:
                installed_count += 1
                path = entry.path or "unknown"
                try:
                    st = os.stat(path)
                    perms = stat.filemode(st.st_mode)
                except Exception:
                    perms = "?"
                console.print(
                    f"    [green]✓ {entry.name:20s}[/green]  "
                    f"[dim]{path}[/dim]  [dim]{perms}[/dim]"
                )
            else:
                console.print(
                    f"    [red]✗ {entry.name:20s}[/red]  "
                    f"[dim]Install: {entry.install_hint}[/dim]"
                )

    console.print(f"\n[bold]{installed_count}[/bold]/{total_count} tools installed")


# ---------------------------------------------------------------------------
# Subcommand: learn
# ---------------------------------------------------------------------------

def cmd_learn(tool_name: str) -> None:
    """Show beginner-friendly guide for a tool."""
    from whatsmyname.tool_catalog import get_entry

    entry = get_entry(tool_name)
    if not entry:
        console.print(f"[red]Tool '{tool_name}' not found in catalog.[/red]")
        console.print("[dim]Run 'recon inventory' to see all known tools.[/dim]")
        return

    status = "[green]✓ INSTALLED[/green]" if entry.installed else "[red]✗ NOT INSTALLED[/red]"
    console.print(Panel(
        f"[bold red]{entry.name}[/bold red]  {status}\n"
        f"[dim]{entry.category}[/dim]\n\n"
        f"{entry.description}\n\n"
        f"[bold]Command:[/bold] {entry.command}\n"
        f"[bold]Input types:[/bold] {', '.join(entry.input_types)}\n"
        f"[bold]Passive:[/bold] {'Yes ✓' if entry.passive else 'No ✗ (touches target)'}\n"
        + (f"[bold]Path:[/bold] {entry.path}\n" if entry.installed else
           f"[bold]Install:[/bold] {entry.install_hint}\n")
        + (f"[bold]Docs:[/bold] {entry.learn_more}" if entry.learn_more else ""),
        title=f"Learn: {entry.name}",
        border_style="red",
    ))

    if entry.examples:
        console.print(f"\n  [bold]Examples ({len(entry.examples)}):[/bold]")
        for i, ex in enumerate(entry.examples, 1):
            console.print(f"    [bold red]{i}.[/bold red] {ex['desc']}")
            console.print(f"       [green]$ {ex['cmd']}[/green]")
            console.print()

    if entry.works_well_with:
        console.print(f"  [bold]What to run next:[/bold]")
        from whatsmyname.tool_catalog import get_entry as _get
        for w in entry.works_well_with:
            companion = _get(w["tool"])
            inst = "[green]✓[/green]" if (companion and companion.installed) else "[red]✗[/red]"
            console.print(f"    {inst} [red]{w['tool']}[/red] — {w['reason']}")
        console.print()


# ---------------------------------------------------------------------------
# Subcommand: suggest
# ---------------------------------------------------------------------------

def cmd_suggest(tool_name: str) -> None:
    """Show what to run next after using a tool."""
    from whatsmyname.workflows import suggest_next_tools

    suggestions = suggest_next_tools(tool_name)
    if not suggestions:
        console.print(f"[yellow]No suggestions found for '{tool_name}'.[/yellow]")
        return

    console.print(f"\n  [bold]After using [red]{tool_name}[/red], consider:[/bold]\n")
    for s in suggestions:
        inst = "[green]✓[/green]" if s.get("installed") else "[red]✗[/red]"
        console.print(f"    {inst} [red]{s['tool']}[/red]")
        console.print(f"       {s['reason']}")
        if s.get("install_hint"):
            console.print(f"       [dim]Install: {s['install_hint']}[/dim]")
        console.print()


# ---------------------------------------------------------------------------
# Subcommand: categories
# ---------------------------------------------------------------------------

def cmd_categories() -> None:
    """List all tool categories with counts."""
    from whatsmyname.tool_catalog import get_by_category

    cats = get_by_category()
    table = Table(title="Tool Categories", border_style="dim", expand=True)
    table.add_column("Category", style="magenta")
    table.add_column("Total", justify="right")
    table.add_column("Installed", justify="right", style="green")
    table.add_column("Missing", justify="right", style="red")

    for cat_name in sorted(cats.keys()):
        entries = cats[cat_name]
        installed = sum(1 for e in entries if e.installed)
        missing = len(entries) - installed
        table.add_row(cat_name, str(len(entries)), str(installed), str(missing))

    console.print(table)


# ---------------------------------------------------------------------------
# Subcommand: workflows
# ---------------------------------------------------------------------------

def cmd_workflows() -> None:
    """Show investigation workflow templates."""
    from whatsmyname.workflows import get_workflows

    workflows = get_workflows()
    for wf in workflows:
        console.print(Panel(
            f"[bold]{wf['description']}[/bold]\n"
            f"[dim]Input type: {wf['input_type']}  |  Tags: {', '.join(wf.get('tags', []))}[/dim]",
            title=f"[red]{wf['name']}[/red]",
            border_style="dim",
        ))
        for i, step in enumerate(wf["steps"], 1):
            inst = "[green]✓[/green]" if step.get("installed") else "[red]✗[/red]"
            console.print(f"    {inst} [bold]{i}.[/bold] [red]{step['tool']}[/red] — {step['desc']}")
        console.print()


# ---------------------------------------------------------------------------
# Subcommand: list-tools (enhanced)
# ---------------------------------------------------------------------------

def cmd_list_tools() -> None:
    tools = build_tool_configs()
    table = Table(title="Supported OSINT Tools", border_style="dim", expand=True)
    table.add_column("Tool", style="red")
    table.add_column("Command")
    table.add_column("Input Types")
    table.add_column("Status")
    table.add_column("Description", style="dim")

    for t in tools:
        status_str = "[green]✓ installed[/green]" if t.enabled else "[red]✗ missing[/red]"
        types = ", ".join(it.value for it in t.input_types)
        table.add_row(t.name, t.command, types, status_str, t.description)

    console.print(table)

    installed = sum(1 for t in tools if t.enabled)
    console.print(f"\n[bold]{installed}[/bold]/{len(tools)} tools installed")

    try:
        from whatsmyname.plugin_loader import list_plugins
        plugins = list_plugins()
        if plugins:
            console.print(f"\n[bold]Plugins ({len(plugins)}):[/bold]")
            for p in plugins:
                console.print(f"  {p['file']} — {p['count']} tools")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Subcommand: plugins (marketplace)
# ---------------------------------------------------------------------------

def _handle_plugins(args: list[str]) -> None:
    """Handle all plugins subcommands."""
    from whatsmyname.plugin_loader import (
        list_plugins, install_sample_plugin,
        marketplace_search, marketplace_install, marketplace_uninstall,
        validate_plugin, scaffold_plugin, marketplace_submit,
    )

    if not args or args[0] == "list":
        # Default: show installed plugins
        install_sample_plugin()
        plugins = list_plugins()
        if not plugins:
            console.print("[yellow]No active plugins in ~/.recon/plugins/[/yellow]")
            console.print("[dim]Browse the marketplace: recon plugins search[/dim]")
            console.print("[dim]Install a plugin:       recon plugins install <name>[/dim]")
            console.print("[dim]Create a new plugin:    recon plugins create <name>[/dim]")
        else:
            table = Table(title="Installed Plugins", border_style="dim")
            table.add_column("File", style="red")
            table.add_column("Tools")
            table.add_column("Status")
            for p in plugins:
                status_str = "[green]\u2713 ok[/green]" if p["status"] == "ok" else f"[red]\u2717 {p['status']}[/red]"
                table.add_row(p["file"], ", ".join(p["tools"]), status_str)
            console.print(table)
        return

    action = args[0]

    if action == "search":
        query = args[1] if len(args) > 1 else None
        console.print("[dim]Fetching marketplace registry...[/dim]")
        results = marketplace_search(query)
        if not results:
            console.print("[yellow]No plugins found.[/yellow]")
            return
        table = Table(title="Plugin Marketplace", border_style="red", expand=True)
        table.add_column("Name", style="bold red")
        table.add_column("Description")
        table.add_column("Category", style="dim")
        table.add_column("Tier")
        table.add_column("Version", justify="right", style="dim")
        for p in results:
            tier = "[green]FREE[/green]" if p.get("tier") == "free" else f"[yellow]${p.get('price', '?')}[/yellow]"
            table.add_row(p["name"], p["description"][:60], p.get("category", ""), tier, p.get("version", ""))
        console.print(table)
        console.print(f"\n[dim]Install with: recon plugins install <name>[/dim]")

    elif action == "install":
        if len(args) < 2:
            console.print("[red]Usage: recon plugins install <plugin-name> [--key KEY][/red]")
            console.print("[dim]Browse: recon plugins search[/dim]")
            return
        name = args[1]
        # Parse --key flag
        license_key = None
        for i, a in enumerate(args):
            if a == "--key" and i + 1 < len(args):
                license_key = args[i + 1]
                break
        console.print(f"[dim]Installing {name}...[/dim]")
        result = marketplace_install(name, license_key=license_key)
        if result["success"]:
            console.print(f"[green]\u2713 Installed {result['plugin']} v{result['version']}[/green]")
            console.print(f"[dim]  Path: {result['path']}[/dim]")
            if result.get("tools"):
                console.print(f"[dim]  Tools added: {', '.join(result['tools'])}[/dim]")
        elif result.get("needs_license"):
            console.print(f"[yellow]\u26a0 {result['error']}[/yellow]")
            if result.get("purchase_url"):
                console.print(f"[bold]Purchase: {result['purchase_url']}[/bold]")
            console.print(f"[dim]{result.get('hint', '')}[/dim]")
        else:
            console.print(f"[red]\u2717 {result['error']}[/red]")

    elif action in ("uninstall", "remove"):
        if len(args) < 2:
            console.print("[red]Usage: recon plugins uninstall <plugin-name>[/red]")
            return
        name = args[1]
        result = marketplace_uninstall(name)
        if result["success"]:
            console.print(f"[green]\u2713 Removed {result['plugin']}[/green]")
        else:
            console.print(f"[red]\u2717 {result['error']}[/red]")

    elif action == "create":
        if len(args) < 2:
            console.print("[red]Usage: recon plugins create <plugin-name>[/red]")
            return
        name = args[1]
        result = scaffold_plugin(name)
        if result["success"]:
            console.print(f"[green]\u2713 Created plugin scaffold: {result['path']}[/green]")
            console.print(f"[dim]  Edit the file, then test locally:[/dim]")
            console.print(f"[dim]    cp {result['path']} ~/.recon/plugins/[/dim]")
            console.print(f"[dim]    recon list-tools[/dim]")
            console.print(f"[dim]  When ready, validate and submit:[/dim]")
            console.print(f"[dim]    recon plugins validate {result['path']}[/dim]")
            console.print(f"[dim]    recon plugins submit {result['path']}[/dim]")
        else:
            console.print(f"[red]\u2717 {result['error']}[/red]")

    elif action == "validate":
        if len(args) < 2:
            console.print("[red]Usage: recon plugins validate <file.py>[/red]")
            return
        filepath = args[1]
        console.print(f"[dim]Validating {filepath}...[/dim]")
        result = validate_plugin(filepath)
        if result["valid"]:
            console.print(f"[green]\u2713 Plugin is valid[/green]")
            meta = result["metadata"]
            if meta:
                console.print(f"[dim]  Name:       {meta.get('name', 'N/A')}[/dim]")
                console.print(f"[dim]  Category:   {meta.get('category', 'N/A')}[/dim]")
                console.print(f"[dim]  Tools:      {', '.join(meta.get('tools_provided', []))}[/dim]")
                console.print(f"[dim]  Inputs:     {', '.join(meta.get('input_types', []))}[/dim]")
            for w in result["warnings"]:
                console.print(f"[yellow]  \u26a0 {w}[/yellow]")
            console.print(f"\n[dim]Submit with: recon plugins submit {filepath}[/dim]")
        else:
            console.print(f"[red]\u2717 Validation failed[/red]")
            for e in result["errors"]:
                console.print(f"[red]  \u2717 {e}[/red]")
            for w in result["warnings"]:
                console.print(f"[yellow]  \u26a0 {w}[/yellow]")

    elif action == "submit":
        if len(args) < 2:
            console.print("[red]Usage: recon plugins submit <file.py> [--tier paid --price 10][/red]")
            return
        filepath = args[1]
        # Parse --tier and --price flags
        tier = "free"
        price = 0.0
        for i, a in enumerate(args):
            if a == "--tier" and i + 1 < len(args):
                tier = args[i + 1]
            elif a == "--price" and i + 1 < len(args):
                try:
                    price = float(args[i + 1])
                except ValueError:
                    console.print("[red]--price must be a number[/red]")
                    return
        console.print(f"[dim]Validating and submitting {filepath}...[/dim]")
        result = marketplace_submit(filepath, tier=tier, price=price)
        if result["success"]:
            console.print(f"[green]\u2713 Plugin submitted: {result['plugin']}[/green]")
            console.print(f"[bold]Issue: {result['issue_url']}[/bold]")
            console.print("[dim]The maintainer will review and add it to the marketplace.[/dim]")
        else:
            console.print(f"[red]\u2717 {result['error']}[/red]")
            if result.get("validation_errors"):
                for e in result["validation_errors"]:
                    console.print(f"[red]  \u2717 {e}[/red]")

    else:
        console.print(f"[red]Unknown plugins command: {action}[/red]")
        console.print("[dim]Available: list, search, install, uninstall, create, validate, submit[/dim]")


# ---------------------------------------------------------------------------
# Subcommand: update
# ---------------------------------------------------------------------------

def cmd_update(extra_args: list[str] | None = None) -> None:
    """Update all OSINT tools, dependencies, and RECON itself."""
    update_script = Path.home() / ".local" / "bin" / "recon-update"
    if not update_script.exists():
        # Fallback to RECON_HOME
        recon_home = os.environ.get("RECON_HOME", str(Path.home() / "RECON_WorkBench"))
        update_script = Path(recon_home) / "update.sh"

    if update_script.exists():
        cmd = ["bash", str(update_script)] + (extra_args or [])
        subprocess.run(cmd)
    else:
        console.print("[red]Update script not found.[/red]")
        console.print("[dim]Reinstall with: bash ~/RECON_WorkBench/install.sh[/dim]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Async scan engine
# ---------------------------------------------------------------------------

async def _async_main(args: argparse.Namespace) -> None:
    input_type = None
    if args.type:
        input_type = InputType(args.type)

    detected = input_type or detect_input_type(args.target)

    # --- Dry run ---
    if args.dry_run:
        all_tools = build_tool_configs()
        applicable = [t for t in all_tools if detected in t.input_types and t.enabled]
        if args.tools:
            override = {n.strip().lower() for n in args.tools.split(",")}
            applicable = [t for t in applicable if t.name.lower() in override]

        console.print(f"[bold]Dry Run — would execute:[/bold]")
        console.print(f"[bold]Target:[/bold]  {args.target}")
        console.print(f"[bold]Type:[/bold]    {detected.value}")
        console.print()
        for t in applicable:
            try:
                cmd_args = t.build_args(args.target, "/tmp/recon_dry")
                full_cmd = [t.command] + [str(a) for a in cmd_args]
                console.print(f"  [red]{t.name}[/red]")
                console.print(f"    [green]$ {' '.join(full_cmd)}[/green]")
                console.print(f"    [dim]timeout: {t.timeout}s[/dim]")
            except Exception as e:
                console.print(f"  [red]{t.name}[/red]  [red]error building args: {e}[/red]")
        return

    # Print header
    console.print(f"[bold]Target:[/bold]  {args.target}")
    console.print(f"[bold]Type:[/bold]    {detected.value}")

    tools_override = None
    if args.tools:
        tools_override = [t.strip() for t in args.tools.split(",")]
        console.print(f"[bold]Tools:[/bold]   {', '.join(tools_override)}")

    email_expand = not args.no_email_expand
    if detected == InputType.USERNAME and email_expand:
        console.print(f"[bold]Email expansion:[/bold] ON")

    console.print()

    # Track tool states for live display
    lock = Lock()
    tool_states: dict[str, str] = {}
    tool_findings: dict[str, int] = {}
    tool_elapsed: dict[str, float] = {}

    all_tools = build_tool_configs()
    applicable = [t for t in all_tools if detected in t.input_types and t.enabled]
    if tools_override:
        override_lower = {n.lower() for n in tools_override}
        applicable = [t for t in applicable if t.name.lower() in override_lower]

    for t in applicable:
        tool_states[t.name] = "waiting"

    if detected == InputType.USERNAME and email_expand:
        email_tools = [t for t in all_tools if InputType.EMAIL in t.input_types and t.enabled]
        if tools_override:
            override_lower = {n.lower() for n in tools_override}
            email_tools = [t for t in email_tools if t.name.lower() in override_lower]
        for et in email_tools:
            key = f"{et.name} (email)"
            tool_states[key] = "waiting"

    def on_start(name: str) -> None:
        with lock:
            if name in tool_states:
                tool_states[name] = "running"
            else:
                for k in tool_states:
                    if k.startswith(name) and tool_states[k] == "waiting":
                        tool_states[k] = "running"
                        break

    def on_finish(name: str, report: ToolReport) -> None:
        with lock:
            key = name
            if name not in tool_states:
                for k in tool_states:
                    if k.startswith(name) and tool_states[k] == "running":
                        key = k
                        break
            tool_states[key] = report.status
            tool_findings[key] = len(report.findings)
            tool_elapsed[key] = report.elapsed

    start_time = time.monotonic()

    with Live(
        _build_status_table(tool_states, tool_findings, tool_elapsed),
        console=console, refresh_per_second=4, transient=True,
    ) as live:
        async def update_display():
            while True:
                await asyncio.sleep(0.25)
                live.update(_build_status_table(tool_states, tool_findings, tool_elapsed))

        display_task = asyncio.create_task(update_display())
        try:
            report = await run_recon(
                target=args.target,
                input_type=input_type,
                tools_override=tools_override,
                email_expand=email_expand,
                timeout_override=args.timeout,
                on_start=on_start,
                on_finish=on_finish,
            )
        finally:
            display_task.cancel()
            try:
                await display_task
            except asyncio.CancelledError:
                pass

    total_time = time.monotonic() - start_time
    console.print(f"\n[bold]Scan completed in {total_time:.1f}s[/bold]\n")

    _print_results(report)

    # --- Exposure score ---
    if args.score:
        from whatsmyname.enrichment import calculate_exposure_score
        deduped = report.deduplicated_findings()
        findings_dicts = [
            {"url": f.url, "site_name": f.site_name, "category": f.category,
             "source_tool": f.source_tool}
            for f in deduped
        ]
        score_result = calculate_exposure_score(findings_dicts)
        color = "red" if score_result["score"] >= 60 else "yellow" if score_result["score"] >= 30 else "green"
        console.print(Panel(
            f"[bold {color}]{score_result['score']}/100[/bold {color}]  "
            f"[bold]{score_result['rating']}[/bold]\n\n"
            + "\n".join(f"  {k}: {v}" for k, v in score_result["breakdown"].items()),
            title="Exposure Score",
            border_style=color,
        ))

    # --- Post-scan suggestions ---
    if args.discover:
        from whatsmyname.workflows import suggest_after_scan
        tools_run = [t.tool_name for t in report.tools_run if t.status == "completed"]
        cats = list(report.by_category().keys())
        suggestions = suggest_after_scan(detected.value, tools_run, cats)

        if suggestions["next_suggestions"]:
            console.print("\n[bold]💡 Suggested next tools:[/bold]")
            for s in suggestions["next_suggestions"]:
                console.print(f"  [red]{s['tool']}[/red] — {s['reason']}")

    # --- Export ---
    if args.output:
        ext = args.output
        default_name = f"{args.target}.{ext}"
        out_path = args.output_file or default_name

        if ext == "json":
            export_json(report, out_path)
        elif ext == "csv":
            export_csv(report, out_path)
        elif ext == "html":
            export_html(report, out_path)

        console.print(f"\n[green]Report saved to {out_path}[/green]")

        if args.open and ext == "html":
            webbrowser.open(f"file://{os.path.abspath(out_path)}")

    # --- Session tracking ---
    if args.session:
        from whatsmyname.sessions import create_or_resume, save_session, SessionRun
        from datetime import datetime, timezone
        session = create_or_resume(args.session)
        if args.case_id:
            session.case_id = args.case_id
        if args.examiner:
            session.examiner = args.examiner
        run = SessionRun(
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=args.target,
            input_type=detected.value,
            tools_run=[t.tool_name for t in report.tools_run if t.status != "not_installed"],
            findings_count=len(report.all_findings),
            categories_found=list(report.by_category().keys()),
            elapsed=total_time,
            notes=args.notes or "",
            case_id=args.case_id or "",
        )
        session.add_run(run)
        deduped = report.deduplicated_findings()
        session.add_findings([
            {"url": f.url, "site_name": f.site_name, "category": f.category,
             "source_tool": f.source_tool}
            for f in deduped
        ])
        if args.notes:
            session.add_note(args.notes)
        path = save_session(session)
        console.print(f"\n[green]Session '{args.session}' saved ({session.total_runs} runs, {session.total_findings} findings)[/green]")

    # --- Desktop notification ---
    if args.notify:
        try:
            deduped = report.deduplicated_findings()
            subprocess.run([
                "osascript", "-e",
                f'display notification "Found {len(deduped)} results for {args.target}" '
                f'with title "Project RECON"',
            ], capture_output=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    # Handle subcommands before argparse
    raw_args = argv if argv is not None else sys.argv[1:]

    if raw_args and raw_args[0] in ("inventory", "learn", "suggest", "categories",
                                     "workflows", "templates", "plugins", "update", "shell"):
        subcmd = raw_args[0]

        if subcmd == "inventory":
            cmd_inventory()
        elif subcmd == "learn":
            if len(raw_args) < 2:
                console.print("[red]Usage: recon learn <tool_name>[/red]")
                sys.exit(1)
            cmd_learn(raw_args[1])
        elif subcmd == "suggest":
            if len(raw_args) < 2:
                console.print("[red]Usage: recon suggest <tool_name>[/red]")
                sys.exit(1)
            cmd_suggest(raw_args[1])
        elif subcmd == "categories":
            cmd_categories()
        elif subcmd == "workflows":
            cmd_workflows()
        elif subcmd == "templates":
            from whatsmyname.templates import list_templates
            templates = list_templates()
            table = Table(title="Scan Templates", border_style="dim", expand=True)
            table.add_column("Name", style="red")
            table.add_column("Description")
            table.add_column("Tools")
            table.add_column("Tags", style="dim")
            for t in templates:
                tools_str = ", ".join(t["tools"][:5])
                if len(t["tools"]) > 5:
                    tools_str += f" +{len(t['tools']) - 5} more"
                table.add_row(t["name"], t["description"], tools_str, ", ".join(t["tags"]))
            console.print(table)
        elif subcmd == "plugins":
            _handle_plugins(raw_args[1:])
        elif subcmd == "update":
            cmd_update(raw_args[1:])
        elif subcmd == "shell":
            from whatsmyname.shell import run_shell
            run_shell()
        return

    # Standard argparse for scan mode
    args = parse_args(argv)

    if not args.no_banner:
        console.print(BANNER)

    if args.list_tools:
        cmd_list_tools()
        return

    # Handle --cheatsheet
    if args.cheatsheet:
        cmd_learn(args.cheatsheet)
        return

    if not args.target:
        console.print("[red]Error:[/red] target argument is required. Run [red]recon --help[/red] for usage.")
        sys.exit(1)

    # Apply template if specified
    if args.template:
        from whatsmyname.templates import get_template
        tmpl = get_template(args.template)
        if not tmpl:
            console.print(f"[red]Unknown template: {args.template}[/red]")
            console.print("[dim]Run 'recon templates' to see available profiles.[/dim]")
            sys.exit(1)
        if tmpl.tools and not args.tools:
            args.tools = ",".join(tmpl.tools)
        if tmpl.deep:
            args.deep = True
        if tmpl.quick:
            args.quick = True
        if tmpl.passive_only:
            args.passive = True
        if not args.no_email_expand:
            args.no_email_expand = not tmpl.email_expand
        console.print(f"[dim]Using template: {tmpl.name} — {tmpl.description}[/dim]")

    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main()
