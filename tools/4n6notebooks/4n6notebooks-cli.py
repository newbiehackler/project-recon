#!/usr/bin/env python3
"""
4n6notebooks CLI — RECON iOS Forensics Notebook Launcher

Launch and manage Jupyter forensic analysis notebooks for iOS device
forensics: SQLCipher decryption, Signal parsing, ProtonMail recovery,
chat rendering, and media extraction.

Part of Project RECON — Rapid Evidence Collection & OSINT Network
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
SRC_DIR = TOOL_DIR / "src"
VERSION = "1.0.0"

BANNER = r"""
  ██╗  ██╗███╗   ██╗ ██████╗
  ██║  ██║████╗  ██║██╔════╝
  ███████║██╔██╗ ██║███████╗
  ╚════██║██║╚██╗██║██╔═══██╗
       ██║██║ ╚████║╚██████╔╝
       ╚═╝╚═╝  ╚═══╝ ╚═════╝
  iOS Forensics Notebooks — RECON Module
"""

HELP_EPILOG = textwrap.dedent("""\

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     4N6NOTEBOOKS — iOS Forensics Analysis for RECON
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    OVERVIEW
    ────────
      Interactive Jupyter notebooks for iOS device forensic analysis.
      Each notebook provides step-by-step guided analysis with code
      cells you can modify for your specific case.

    AVAILABLE NOTEBOOKS
    ───────────────────
      1. SQLCipher Decrypt
         Decrypt databases encrypted with SQLCipher (used by Signal,
         WhatsApp, and many other iOS apps).
         Dependencies: PyCryptodome

      2. iOS Signal Parsing
         Decrypt and parse the Signal messaging database from an iOS
         backup. Renders conversations as interactive HTML.
         Dependencies: PyCryptodome, Pandas

      3. iOS ProtonMail
         Decrypt, parse and render ProtonMail messages from iOS.
         Handles PGP decryption of message bodies.
         Dependencies: PyCryptodome, pgpy, Pandas

      4. Chat Rendering
         Convert extracted chat data into visual HTML that looks like
         a real messaging app (with timestamps, avatars, media).
         Dependencies: Pandas

      5. iOS Media Extraction
         Extract photos and videos from iOS filesystem dumps (tar/zip).
         Generates a browsable gallery with thumbnails.
         Dependencies: Pillow, ffmpeg

    SUBCOMMANDS
    ───────────
      launch [notebook]    Open a specific notebook or the full lab
      list                 List all available notebooks
      install-deps         Install Python dependencies for notebooks
      export <notebook>    Export a notebook to HTML/PDF

    EXAMPLES
    ────────
      # Launch the full forensics lab (all notebooks)
      4n6notebooks launch

      # Launch a specific notebook
      4n6notebooks launch signal
      4n6notebooks launch sqlcipher
      4n6notebooks launch protonmail
      4n6notebooks launch chat-render
      4n6notebooks launch media

      # List available notebooks
      4n6notebooks list

      # Install all dependencies
      4n6notebooks install-deps

      # Export a completed notebook to HTML
      4n6notebooks export signal --format html

    INVESTIGATION WORKFLOW
    ──────────────────────
      1. Obtain iOS backup/filesystem dump
      2. Launch appropriate notebook:  4n6notebooks launch signal
      3. Follow the guided cells in Jupyter
      4. Modify file paths to point to your evidence
      5. Run cells to decrypt and parse data
      6. Export results:  4n6notebooks export signal --format html

    WORKS WELL WITH
    ────────────────
      • keychain-decrypt  — Decrypt iOS keychain for encryption keys
      • exiftool          — Extract metadata from recovered media
      • strings           — Find interesting text in binary databases
      • testdisk          — Recover deleted files from device images
      • compreface        — Run face recognition on extracted photos

    REQUIREMENTS
    ────────────
      • Python 3.7+
      • JupyterLab
      • PyCryptodome, Pandas, Pillow, pgpy
      • ffmpeg (brew install ffmpeg) for video thumbnails

    VERSION
    ───────
      4n6notebooks v1.0.0
      Part of Project RECON v3.0.0

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

NOTEBOOK_MAP = {
    "signal": "iOS_Signal.ipynb",
    "sqlcipher": "SQLCipher_decrypt.ipynb",
    "protonmail": "iOS ProtonMail.ipynb",
    "chat-render": "Signal_parsing.ipynb",
    "media": None,  # placeholder
}


def cmd_launch(args: argparse.Namespace) -> int:
    notebook = getattr(args, "notebook", None)
    target = str(SRC_DIR)

    if notebook and notebook in NOTEBOOK_MAP:
        nb_file = NOTEBOOK_MAP[notebook]
        if nb_file:
            nb_path = SRC_DIR / nb_file
            if nb_path.exists():
                target = str(nb_path)
            else:
                print(f"⚠ Notebook {nb_file} not found, launching lab directory")

    print(f"Launching JupyterLab...")
    print(f"  Location: {target}")
    print(f"  Press Ctrl+C to stop the server")
    cmd = [sys.executable, "-m", "jupyter", "lab", target, "--no-browser"]
    try:
        return subprocess.run(cmd, cwd=str(SRC_DIR)).returncode
    except KeyboardInterrupt:
        print("\n✓ JupyterLab stopped")
        return 0


def cmd_list(args: argparse.Namespace) -> int:
    print("Available forensic notebooks:\n")
    notebooks = [
        ("signal", "iOS_Signal.ipynb", "Decrypt & parse Signal messages"),
        ("sqlcipher", "SQLCipher_decrypt.ipynb", "Decrypt SQLCipher databases"),
        ("protonmail", "iOS ProtonMail.ipynb", "Decrypt ProtonMail messages"),
        ("chat-render", "Signal_parsing.ipynb", "Render chats as HTML"),
    ]
    for name, filename, desc in notebooks:
        path = SRC_DIR / filename
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {name:15s} {filename:30s} {desc}")
    return 0


def cmd_install_deps(args: argparse.Namespace) -> int:
    req_file = SRC_DIR / "requirements.txt"
    if not req_file.exists():
        print("✗ requirements.txt not found")
        return 1
    print("Installing 4n6notebooks dependencies...")
    return subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)]).returncode


def cmd_export(args: argparse.Namespace) -> int:
    notebook = args.notebook
    fmt = getattr(args, "format", "html")
    nb_file = NOTEBOOK_MAP.get(notebook)
    if not nb_file:
        print(f"✗ Unknown notebook: {notebook}")
        return 1
    nb_path = SRC_DIR / nb_file
    if not nb_path.exists():
        print(f"✗ Notebook not found: {nb_path}")
        return 1
    print(f"Exporting {nb_file} to {fmt}...")
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", fmt, str(nb_path)]
    return subprocess.run(cmd).returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="4n6notebooks",
        description="4n6notebooks — iOS Forensics Analysis Notebooks for RECON",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"4n6notebooks {VERSION}")
    sub = parser.add_subparsers(dest="command", title="subcommands")

    p_launch = sub.add_parser("launch", help="Open forensic notebooks in JupyterLab")
    p_launch.add_argument("notebook", nargs="?", choices=list(NOTEBOOK_MAP.keys()),
                          help="Specific notebook to open")

    sub.add_parser("list", help="List available notebooks")
    sub.add_parser("install-deps", help="Install Python dependencies")

    p_export = sub.add_parser("export", help="Export a notebook to HTML/PDF")
    p_export.add_argument("notebook", choices=list(NOTEBOOK_MAP.keys()))
    p_export.add_argument("--format", choices=["html", "pdf"], default="html")

    args = parser.parse_args()
    handlers = {
        "launch": cmd_launch, "list": cmd_list,
        "install-deps": cmd_install_deps, "export": cmd_export,
    }

    if not args.command:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
