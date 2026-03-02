"""Output formatters — terminal (rich), JSON, CSV, HTML."""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from whatsmyname.checker import CheckResult, Status

console = Console()


# ---------------------------------------------------------------------------
# Terminal / Rich output
# ---------------------------------------------------------------------------


def create_progress(total: int) -> Progress:
    """Create a rich progress bar for site checking."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Scanning"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


def print_banner(username: str, site_count: int) -> None:
    console.print()
    console.print("[bold cyan]╔══════════════════════════════════════════╗[/]")
    console.print("[bold cyan]║[/]  [bold white]WhatsMyName[/] — Username Enumeration      [bold cyan]║[/]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/]")
    console.print(f"  [dim]Target:[/]  [bold yellow]{username}[/]")
    console.print(f"  [dim]Sites:[/]   [bold]{site_count:,}[/]")
    console.print()


def print_result_line(result: CheckResult, verbose: bool = False) -> None:
    """Print a single result line during scanning."""
    if result.status == Status.FOUND:
        url = result.pretty_url or result.url
        console.print(
            f"  [bold green]✓[/] [green]{result.site_name}[/]"
            f"  [dim]({result.category})[/]"
            f"  [underline blue]{url}[/]"
        )
    elif verbose and result.status == Status.ERROR:
        console.print(
            f"  [bold yellow]![/] [yellow]{result.site_name}[/]"
            f"  [dim]{result.error}[/]"
        )


def print_summary(results: list[CheckResult], elapsed: float) -> None:
    """Print summary table after all checks complete."""
    found = [r for r in results if r.status == Status.FOUND]
    errors = [r for r in results if r.status == Status.ERROR]
    not_found = [r for r in results if r.status == Status.NOT_FOUND]

    console.print()
    console.print("[bold]═══ Summary ═══[/]")
    console.print(
        f"  [green]Found:[/] {len(found)}   "
        f"[red]Not Found:[/] {len(not_found)}   "
        f"[yellow]Errors:[/] {len(errors)}   "
        f"[dim]Time:[/] {elapsed:.1f}s"
    )

    if found:
        console.print()

        # Group by category
        by_cat: dict[str, list[CheckResult]] = {}
        for r in sorted(found, key=lambda x: (x.category, x.site_name)):
            by_cat.setdefault(r.category, []).append(r)

        table = Table(title="Accounts Found", show_lines=False, pad_edge=False)
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Site", style="green")
        table.add_column("URL", style="blue")
        table.add_column("Time", style="dim", justify="right")

        for cat in sorted(by_cat.keys()):
            for i, r in enumerate(by_cat[cat]):
                url = r.pretty_url or r.url
                table.add_row(
                    cat if i == 0 else "",
                    r.site_name,
                    url,
                    f"{r.response_time:.1f}s",
                )

        console.print(table)

    console.print()


# ---------------------------------------------------------------------------
# File export
# ---------------------------------------------------------------------------


def _results_to_dicts(results: list[CheckResult]) -> list[dict[str, Any]]:
    return [
        {
            "site": r.site_name,
            "url": r.pretty_url or r.url,
            "status": r.status.value,
            "http_code": r.http_code,
            "category": r.category,
            "response_time": round(r.response_time, 3),
            "error": r.error,
        }
        for r in results
    ]


def export_json(
    results: list[CheckResult], username: str, filepath: str | Path
) -> Path:
    """Export results to JSON file."""
    path = Path(filepath)
    found = [r for r in results if r.status == Status.FOUND]
    data = {
        "username": username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "found_count": len(found),
        "total_checked": len(results),
        "results": _results_to_dicts(found),
        "all_results": _results_to_dicts(results),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def export_csv(
    results: list[CheckResult], username: str, filepath: str | Path
) -> Path:
    """Export results to CSV file."""
    path = Path(filepath)
    rows = _results_to_dicts(results)
    if not rows:
        path.write_text("site,url,status,http_code,category,response_time,error\n")
        return path

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_html(
    results: list[CheckResult], username: str, filepath: str | Path
) -> Path:
    """Export results to a self-contained HTML report."""
    path = Path(filepath)
    found = [r for r in results if r.status == Status.FOUND]
    errors = [r for r in results if r.status == Status.ERROR]

    # Group found by category
    by_cat: dict[str, list[CheckResult]] = {}
    for r in sorted(found, key=lambda x: (x.category, x.site_name)):
        by_cat.setdefault(r.category, []).append(r)

    rows_html = []
    for cat in sorted(by_cat.keys()):
        for r in by_cat[cat]:
            url = r.pretty_url or r.url
            rows_html.append(
                f'<tr><td>{cat}</td><td>{r.site_name}</td>'
                f'<td><a href="{url}" target="_blank">{url}</a></td>'
                f'<td>{r.response_time:.1f}s</td></tr>'
            )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WhatsMyName Report — {username}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0d1117; color: #c9d1d9; padding: 2rem; }}
  h1 {{ color: #58a6ff; margin-bottom: .5rem; }}
  .meta {{ color: #8b949e; margin-bottom: 1.5rem; }}
  .stats {{ display: flex; gap: 2rem; margin-bottom: 1.5rem; }}
  .stat {{ background: #161b22; padding: 1rem 1.5rem; border-radius: 8px; }}
  .stat .num {{ font-size: 1.8rem; font-weight: bold; }}
  .stat .label {{ color: #8b949e; font-size: .85rem; }}
  .found .num {{ color: #3fb950; }}
  .errors .num {{ color: #d29922; }}
  table {{ width: 100%; border-collapse: collapse; background: #161b22;
           border-radius: 8px; overflow: hidden; }}
  th {{ background: #21262d; text-align: left; padding: .75rem 1rem;
       color: #8b949e; font-weight: 600; font-size: .85rem; text-transform: uppercase; }}
  td {{ padding: .6rem 1rem; border-top: 1px solid #21262d; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  tr:hover td {{ background: #1c2129; }}
</style>
</head>
<body>
  <h1>WhatsMyName Report</h1>
  <p class="meta">Username: <strong>{username}</strong> &mdash; {timestamp}</p>
  <div class="stats">
    <div class="stat found"><div class="num">{len(found)}</div><div class="label">Found</div></div>
    <div class="stat"><div class="num">{len(results)}</div><div class="label">Checked</div></div>
    <div class="stat errors"><div class="num">{len(errors)}</div><div class="label">Errors</div></div>
  </div>
  <table>
    <thead><tr><th>Category</th><th>Site</th><th>URL</th><th>Time</th></tr></thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</body>
</html>"""

    path.write_text(html, encoding="utf-8")
    return path
