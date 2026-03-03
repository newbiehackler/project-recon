"""CLI entry point for WhatsMyName."""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from collections import Counter
from pathlib import Path

from rich.table import Table

from whatsmyname import __version__
from whatsmyname.checker import CheckerConfig, CheckResult, Status, check_username
from whatsmyname.data_manager import (
    load_all_local,
    load_all_with_update,
)
from whatsmyname.reporter import (
    console,
    create_progress,
    export_csv,
    export_html,
    export_json,
    print_banner,
    print_result_line,
    print_summary,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wmn",
        description=(
            "WhatsMyName — OSINT username enumeration across 10,000+ websites. "
            "Check if a username exists on social media, dating, crypto, gaming, "
            "forums, and thousands of other platforms."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  wmn johndoe                         Basic scan\n"
            "  wmn johndoe --category dating,crypto Scan specific categories\n"
            "  wmn johndoe --output json            Export as JSON\n"
            "  wmn johndoe --nsfw                   Include NSFW sites\n"
            "  wmn johndoe --tor                    Route through Tor\n"
            "  wmn johndoe --workers 200            Faster with more workers\n"
            "  wmn --update                         Fetch latest site data\n"
            "  wmn --list-categories                Show all categories\n"
            "  wmn --stats                          Show data source statistics\n"
        ),
    )

    p.add_argument(
        "username",
        nargs="?",
        help="Username to search for across all sites.",
    )

    # --- Output options ---
    out = p.add_argument_group("output options")
    out.add_argument(
        "-o", "--output",
        choices=["json", "csv", "html"],
        help="Export results to file. File is saved as <username>.<format>.",
    )
    out.add_argument(
        "--output-file",
        metavar="PATH",
        help="Custom output file path (overrides default naming).",
    )
    out.add_argument(
        "--found-only",
        action="store_true",
        help="Only show sites where the username was found.",
    )
    out.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show errors and extra details during scan.",
    )
    out.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output.",
    )
    out.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip the banner display.",
    )

    # --- Filtering ---
    filt = p.add_argument_group("filtering")
    filt.add_argument(
        "-c", "--category",
        metavar="CAT",
        help=(
            "Comma-separated list of categories to include. "
            "Use --list-categories to see all options."
        ),
    )
    filt.add_argument(
        "--exclude-category",
        metavar="CAT",
        help="Comma-separated list of categories to exclude.",
    )
    filt.add_argument(
        "--nsfw",
        action="store_true",
        help='Include NSFW sites (excluded by default).',
    )
    filt.add_argument(
        "--site",
        metavar="NAME",
        action="append",
        help="Only check specific site(s). Can be repeated.",
    )

    # --- Connection ---
    conn = p.add_argument_group("connection")
    conn.add_argument(
        "-t", "--timeout",
        type=int,
        default=15,
        metavar="SEC",
        help="Request timeout in seconds (default: 15).",
    )
    conn.add_argument(
        "-w", "--workers",
        type=int,
        default=100,
        metavar="N",
        help="Max concurrent requests (default: 100).",
    )
    conn.add_argument(
        "--proxy",
        metavar="URL",
        help="Proxy URL (e.g. socks5://127.0.0.1:1080, http://proxy:8080).",
    )
    conn.add_argument(
        "--tor",
        action="store_true",
        help="Route requests through Tor (requires Tor running on port 9050).",
    )
    conn.add_argument(
        "--retries",
        type=int,
        default=1,
        metavar="N",
        help="Number of retries per site on failure (default: 1).",
    )

    # --- Data management ---
    data = p.add_argument_group("data management")
    data.add_argument(
        "--update",
        action="store_true",
        help="Fetch latest site data from Sherlock and Maigret projects.",
    )
    data.add_argument(
        "--list-sites",
        action="store_true",
        help="List all available sites and exit.",
    )
    data.add_argument(
        "--list-categories",
        action="store_true",
        help="List all categories and exit.",
    )
    data.add_argument(
        "--stats",
        action="store_true",
        help="Show data source statistics and exit.",
    )

    # --- Misc ---
    p.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return p


def _filter_sites(
    sites: list[dict],
    categories: list[str] | None = None,
    exclude_categories: list[str] | None = None,
    include_nsfw: bool = False,
    site_names: list[str] | None = None,
) -> list[dict]:
    """Apply category and site name filters."""
    filtered = []
    for s in sites:
        cat = s.get("cat", "misc")

        # NSFW exclusion (unless explicitly included)
        if not include_nsfw and cat == "xx NSFW xx":
            continue

        # Category inclusion filter
        if categories and cat.lower() not in [c.lower() for c in categories]:
            continue

        # Category exclusion filter
        if exclude_categories and cat.lower() in [c.lower() for c in exclude_categories]:
            continue

        # Specific site filter
        if site_names:
            name_lower = s.get("name", "").lower()
            if not any(sn.lower() in name_lower for sn in site_names):
                continue

        # Skip sites with valid=false
        if s.get("valid") is False:
            continue

        filtered.append(s)
    return filtered


async def _cmd_update() -> None:
    """Fetch and cache remote data sources."""
    console.print("[bold blue]Updating data sources...[/]")
    sites, stats = await load_all_with_update()
    console.print(f"  [green]✓[/] WhatsMyName:  {stats['wmn']:>6,} sites")
    console.print(f"  [green]✓[/] Extended:      {stats['extended']:>6,} sites")
    console.print(f"  [green]✓[/] Sherlock:      {stats['sherlock']:>6,} sites")
    console.print(f"  [green]✓[/] Maigret:       {stats['maigret']:>6,} sites")
    console.print(f"  [bold]Total (deduped): {stats['total_merged']:>6,} sites[/]")
    console.print("[green]Data updated and cached.[/]")


def _cmd_list_sites(sites: list[dict]) -> None:
    """List all available sites."""
    table = Table(title=f"Available Sites ({len(sites):,})", show_lines=False)
    table.add_column("#", style="dim", justify="right")
    table.add_column("Site", style="green")
    table.add_column("Category", style="cyan")
    table.add_column("URL Pattern", style="blue", max_width=60)

    for i, s in enumerate(sorted(sites, key=lambda x: x.get("name", "").lower()), 1):
        table.add_row(
            str(i),
            s.get("name", ""),
            s.get("cat", ""),
            s.get("uri_check", ""),
        )
    console.print(table)


def _cmd_list_categories(sites: list[dict]) -> None:
    """List all categories with counts."""
    counter = Counter(s.get("cat", "misc") for s in sites)
    table = Table(title="Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Sites", justify="right", style="green")

    for cat in sorted(counter.keys()):
        table.add_row(cat, f"{counter[cat]:,}")

    table.add_row("[bold]Total[/]", f"[bold]{len(sites):,}[/]")
    console.print(table)


def _cmd_stats(sites: list[dict]) -> None:
    """Show data source statistics."""
    source_counter = Counter(s.get("_source", "unknown") for s in sites)
    cat_counter = Counter(s.get("cat", "misc") for s in sites)

    console.print("[bold]Data Source Statistics[/]")
    console.print()

    t1 = Table(title="By Source")
    t1.add_column("Source", style="cyan")
    t1.add_column("Sites", justify="right", style="green")
    for src in sorted(source_counter.keys()):
        t1.add_row(src, f"{source_counter[src]:,}")
    t1.add_row("[bold]Total[/]", f"[bold]{len(sites):,}[/]")
    console.print(t1)

    console.print()

    t2 = Table(title="By Category")
    t2.add_column("Category", style="cyan")
    t2.add_column("Sites", justify="right", style="green")
    for cat in sorted(cat_counter.keys()):
        t2.add_row(cat, f"{cat_counter[cat]:,}")
    console.print(t2)


async def _cmd_check(
    username: str,
    sites: list[dict],
    args: argparse.Namespace,
) -> None:
    """Run username check across all sites."""

    # Apply filters
    categories = [c.strip() for c in args.category.split(",")] if args.category else None
    exclude_cats = (
        [c.strip() for c in args.exclude_category.split(",")]
        if args.exclude_category
        else None
    )
    filtered = _filter_sites(
        sites,
        categories=categories,
        exclude_categories=exclude_cats,
        include_nsfw=args.nsfw,
        site_names=args.site,
    )

    if not filtered:
        console.print("[red]No sites match your filters.[/]")
        sys.exit(1)

    if not args.no_banner:
        print_banner(username, len(filtered))

    config = CheckerConfig(
        timeout=args.timeout,
        max_workers=args.workers,
        proxy=args.proxy,
        tor=args.tor,
        retries=args.retries,
    )

    # Progress tracking
    progress = create_progress(len(filtered))
    task_id = progress.add_task("checking", total=len(filtered))

    found_count = 0

    def on_result(result: CheckResult) -> None:
        nonlocal found_count
        progress.advance(task_id)
        if result.status == Status.FOUND:
            found_count += 1
        print_result_line(result, verbose=args.verbose)

    start_time = time.monotonic()

    with progress:
        results = await check_username(
            username=username,
            sites=filtered,
            config=config,
            progress_callback=on_result,
        )

    elapsed = time.monotonic() - start_time

    # Summary
    if not args.found_only:
        print_summary(results, elapsed)
    else:
        found = [r for r in results if r.status == Status.FOUND]
        print_summary(found, elapsed)

    # Export
    if args.output:
        ext = args.output
        if args.output_file:
            out_path = Path(args.output_file)
        else:
            out_path = Path(f"{username}.{ext}")

        if ext == "json":
            export_json(results, username, out_path)
        elif ext == "csv":
            export_csv(results, username, out_path)
        elif ext == "html":
            export_html(results, username, out_path)

        console.print(f"  [dim]Report saved:[/] [bold]{out_path}[/]")


async def _async_main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.no_color:
        console.no_color = True

    # --- Data management commands (no username required) ---
    if args.update:
        await _cmd_update()
        if not args.username:
            return

    # Load sites
    sites = load_all_local()

    if args.list_sites:
        _cmd_list_sites(sites)
        return

    if args.list_categories:
        _cmd_list_categories(sites)
        return

    if args.stats:
        _cmd_stats(sites)
        return

    # --- Username check (username required) ---
    if not args.username:
        parser.print_help()
        sys.exit(1)

    await _cmd_check(args.username, sites, args)


def main() -> None:
    """Main entry point for the wmn CLI."""
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/]")
        sys.exit(130)
