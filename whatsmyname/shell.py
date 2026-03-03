"""
RECON Interactive Shell — REPL for live investigation.

Commands:
  scan <target>         Run OSINT scan on a target
  learn <tool>          Show tool guide and examples
  suggest <tool>        Show what to run next
  inventory             List all tools and install status
  categories            Browse tool categories
  session <name>        Create/resume a session
  sessions              List saved sessions
  note <text>           Add a note to current session
  pivot <finding>       Use a finding as input for the next scan
  history               Show command history
  help                  Show available commands
  exit / quit           Exit the shell
"""

from __future__ import annotations

import asyncio
import readline
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

HISTORY_FILE = Path.home() / ".recon" / "shell_history"

# Commands available in the shell
SHELL_COMMANDS = [
    "scan", "learn", "suggest", "inventory", "categories",
    "session", "sessions", "note", "pivot", "history",
    "workflows", "templates", "plugins", "help", "exit", "quit",
]


def _setup_readline():
    """Configure readline for tab completion and history."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if HISTORY_FILE.exists():
        try:
            readline.read_history_file(str(HISTORY_FILE))
        except Exception:
            pass

    readline.set_history_length(1000)

    # Tab completion
    from whatsmyname.tool_catalog import get_all_entries
    tool_names = [e.name for e in get_all_entries()]
    all_completions = SHELL_COMMANDS + tool_names

    def completer(text, state):
        options = [c for c in all_completions if c.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")


def _save_history():
    """Save readline history."""
    try:
        readline.write_history_file(str(HISTORY_FILE))
    except Exception:
        pass


def _print_help():
    """Print shell help."""
    table = Table(title="Project RECON Shell Commands", border_style="dim", expand=True)
    table.add_column("Command", style="red", min_width=25)
    table.add_column("Description")

    cmds = [
        ("scan <target>", "Run OSINT scan on a target (username, email, phone)"),
        ("scan <target> --tools wmn,sherlock", "Scan with specific tools only"),
        ("learn <tool>", "Show beginner-friendly guide with examples"),
        ("suggest <tool>", "Show what tools to run next and why"),
        ("inventory", "List all forensics tools and their install status"),
        ("categories", "Browse tools by category"),
        ("workflows", "Show investigation workflow templates"),
        ("templates", "List predefined scan profiles"),
        ("plugins", "List loaded plugins"),
        ("session <name>", "Create or resume a named investigation session"),
        ("sessions", "List all saved sessions"),
        ("note <text>", "Add a note to the current session"),
        ("pivot <url_or_email>", "Use a finding as input for the next scan"),
        ("history", "Show command history"),
        ("help", "Show this help"),
        ("exit / quit", "Exit the shell"),
    ]

    for cmd, desc in cmds:
        table.add_row(cmd, desc)

    console.print(table)


def run_shell():
    """Start the interactive RECON shell."""
    from whatsmyname.sessions import Session, create_or_resume, list_sessions, save_session

    _setup_readline()

    console.print(Panel(
        "[bold red]PROJECT RECON[/bold red] [dim]// Interactive Shell[/dim]\n"
        "[dim red]Rapid Evidence Collection & OSINT Network[/dim red]\n"
        "[dim]Type 'help' for commands, 'exit' to quit. Tab completion enabled.[/dim]",
        border_style="red",
    ))

    current_session: Session | None = None

    while True:
        try:
            # Use plain input since rich prompt doesn't work with readline
            session_indicator = f" ({current_session.name})" if current_session else ""
            user_input = input(f"recon{session_indicator}> ").strip()

            if not user_input:
                continue

            parts = user_input.split(None, 1)
            cmd = parts[0].lower()
            args_str = parts[1] if len(parts) > 1 else ""

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting...[/dim]")
            break

        if cmd in ("exit", "quit"):
            if current_session:
                save_session(current_session)
                console.print(f"[green]Session '{current_session.name}' saved.[/green]")
            break

        elif cmd == "help":
            _print_help()

        elif cmd == "history":
            n = readline.get_current_history_length()
            for i in range(max(1, n - 20), n + 1):
                item = readline.get_history_item(i)
                if item:
                    console.print(f"  [dim]{i}[/dim]  {item}")

        elif cmd == "session":
            if not args_str:
                console.print("[red]Usage: session <name>[/red]")
                continue
            current_session = create_or_resume(args_str)
            console.print(f"[green]Session '{args_str}' active "
                          f"({current_session.total_runs} prior runs, "
                          f"{current_session.total_findings} findings)[/green]")

        elif cmd == "sessions":
            sessions = list_sessions()
            if not sessions:
                console.print("[yellow]No saved sessions.[/yellow]")
            else:
                table = Table(title="Saved Sessions", border_style="dim")
                table.add_column("Name", style="red")
                table.add_column("Runs", justify="right")
                table.add_column("Findings", justify="right")
                table.add_column("Targets", justify="right")
                table.add_column("Updated")
                for s in sessions:
                    table.add_row(
                        s["name"], str(s["runs"]), str(s["findings"]),
                        str(s["targets"]), s["updated"][:19],
                    )
                console.print(table)

        elif cmd == "note":
            if not args_str:
                console.print("[red]Usage: note <text>[/red]")
            elif not current_session:
                console.print("[yellow]No active session. Use 'session <name>' first.[/yellow]")
            else:
                current_session.add_note(args_str)
                save_session(current_session)
                console.print(f"[green]Note added to session '{current_session.name}'.[/green]")

        elif cmd == "inventory":
            # Delegate to CLI function
            from whatsmyname.recon_cli import cmd_inventory
            cmd_inventory()

        elif cmd == "categories":
            from whatsmyname.recon_cli import cmd_categories
            cmd_categories()

        elif cmd == "learn":
            if not args_str:
                console.print("[red]Usage: learn <tool_name>[/red]")
            else:
                from whatsmyname.recon_cli import cmd_learn
                cmd_learn(args_str.strip())

        elif cmd == "suggest":
            if not args_str:
                console.print("[red]Usage: suggest <tool_name>[/red]")
            else:
                from whatsmyname.recon_cli import cmd_suggest
                cmd_suggest(args_str.strip())

        elif cmd == "workflows":
            from whatsmyname.recon_cli import cmd_workflows
            cmd_workflows()

        elif cmd == "templates":
            from whatsmyname.templates import list_templates
            templates = list_templates()
            table = Table(title="Scan Templates", border_style="dim", expand=True)
            table.add_column("Name", style="red")
            table.add_column("Description")
            table.add_column("Tags", style="dim")
            for t in templates:
                table.add_row(t["name"], t["description"], ", ".join(t["tags"]))
            console.print(table)

        elif cmd == "plugins":
            from whatsmyname.plugin_loader import list_plugins
            plugins = list_plugins()
            if not plugins:
                console.print("[yellow]No plugins found in ~/.recon/plugins/[/yellow]")
            else:
                for p in plugins:
                    status = "[green]✓[/green]" if p["status"] == "ok" else f"[red]✗ {p['status']}[/red]"
                    console.print(f"  {status} {p['file']} — {p['count']} tools: {', '.join(p['tools'])}")

        elif cmd == "scan":
            if not args_str:
                console.print("[red]Usage: scan <target> [--tools tool1,tool2][/red]")
            else:
                # Parse scan args and run
                from whatsmyname.recon_cli import _async_main, parse_args
                try:
                    scan_args = parse_args(args_str.split())
                    if scan_args.target:
                        asyncio.run(_async_main(scan_args))
                except SystemExit:
                    pass
                except Exception as e:
                    console.print(f"[red]Scan error: {e}[/red]")

        elif cmd == "pivot":
            if not args_str:
                console.print("[red]Usage: pivot <url_or_email_or_username>[/red]")
            else:
                console.print(f"[red]Pivoting on: {args_str}[/red]")
                from whatsmyname.recon_cli import _async_main, parse_args
                try:
                    scan_args = parse_args([args_str])
                    if scan_args.target:
                        asyncio.run(_async_main(scan_args))
                except SystemExit:
                    pass
                except Exception as e:
                    console.print(f"[red]Pivot error: {e}[/red]")

        else:
            console.print(f"[red]Unknown command: {cmd}[/red]. Type 'help' for available commands.")

    _save_history()
