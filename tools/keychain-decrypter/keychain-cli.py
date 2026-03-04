#!/usr/bin/env python3
"""
iOS Keychain Decrypter CLI — RECON Mobile Forensics Wrapper

Decrypt iOS keychains from jailbroken devices. Extracts saved passwords,
certificates, WiFi credentials, and app secrets.

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
SCRIPT = SRC_DIR / "keychain_decrypt.py"
AGENT = SRC_DIR / "keyclass_unwrapper"
VERSION = "1.0.0"

HELP_EPILOG = textwrap.dedent("""\

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     iOS KEYCHAIN DECRYPTER — Mobile Forensics for RECON
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    OVERVIEW
    ────────
      Decrypts the iOS keychain database from a jailbroken device.
      The keychain stores:
        • Saved passwords (Safari, apps)
        • WiFi network credentials
        • VPN configurations
        • App tokens and secrets
        • Certificates and keys
        • Account credentials

    PREREQUISITES
    ─────────────
      • Jailbroken iOS device (tested on iPhone 7, iOS 14.0)
      • SSH access to device (default with checkra1n)
      • iproxy (from libimobiledevice: brew install libimobiledevice)
      • sshpass (brew install esolitos/ipa/sshpass)
      • Xcode (for compiling the on-device agent)

    SUBCOMMANDS
    ───────────
      decrypt              Run the full keychain decryption process
      build-agent          Compile the on-device key unwrapper agent
      upload-agent         Upload the agent to the jailbroken device
      download-db          Download keychain database from device
      install-deps         Install Python dependencies

    STEP-BY-STEP GUIDE
    ──────────────────
      1. Jailbreak the target device (e.g., with checkra1n)

      2. Start USB port forwarding (in a separate terminal):
           iproxy 2222 44

      3. Build the on-device agent (first time only):
           keychain-decrypt build-agent

      4. Upload agent to device:
           keychain-decrypt upload-agent

      5. Download the keychain database:
           keychain-decrypt download-db

      6. UNLOCK THE DEVICE and keep it unlocked!

      7. Run decryption:
           keychain-decrypt decrypt

      8. Output: keychain_decrypted.plist

      9. Clean up (removes agent, shuts down device):
           keychain-decrypt cleanup

    EXAMPLES
    ────────
      # Full automated workflow
      keychain-decrypt decrypt

      # Just build the agent
      keychain-decrypt build-agent

      # Install Python dependencies
      keychain-decrypt install-deps

      # Custom SSH port
      keychain-decrypt decrypt --port 2222

      # Custom SSH password
      keychain-decrypt decrypt --password alpine

    OUTPUT
    ──────
      The decrypted keychain is saved as keychain_decrypted.plist
      containing all stored credentials in readable format.

      View with:
        plutil -p keychain_decrypted.plist
        open keychain_decrypted.plist  (opens in Xcode)

    INVESTIGATION WORKFLOW
    ──────────────────────
      1. Obtain jailbroken device
      2. Decrypt keychain:       keychain-decrypt decrypt
      3. Extract credentials:    plutil -p keychain_decrypted.plist
      4. Check emails in breaches:  recon email@from-keychain.com
      5. Search usernames:          recon username-from-keychain
      6. Decrypt app databases:     4n6notebooks launch sqlcipher

    WORKS WELL WITH
    ────────────────
      • 4n6notebooks    — Use keychain keys to decrypt app databases
      • holehe          — Check extracted emails for service registrations
      • h8mail          — Check extracted emails in breach databases
      • sherlock        — Search extracted usernames across platforms

    SECURITY WARNING
    ────────────────
      This tool handles extremely sensitive data. Ensure:
        • Proper legal authorization before use
        • Chain of custody documentation
        • Secure storage of decrypted output
        • Evidence bag for forensic integrity

    REQUIREMENTS
    ────────────
      • macOS (Catalina+) or Linux
      • Python 3.7+, pandas, pyasn1, pycrypto
      • Xcode (for agent compilation)
      • libimobiledevice (brew install libimobiledevice)
      • sshpass (brew install esolitos/ipa/sshpass)

    VERSION
    ───────
      keychain-decrypt v1.0.0
      Part of Project RECON v3.0.0

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def cmd_decrypt(args: argparse.Namespace) -> int:
    if not SCRIPT.exists():
        print(f"✗ keychain_decrypt.py not found at {SCRIPT}", file=sys.stderr)
        return 1
    print("Running keychain decryption...")
    print("  ⚠ Make sure the device is UNLOCKED and iproxy is running")
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=str(SRC_DIR)).returncode


def cmd_build_agent(args: argparse.Namespace) -> int:
    makefile = SRC_DIR / "Makefile"
    if not makefile.exists():
        print("✗ Makefile not found")
        return 1
    print("Building on-device agent...")
    result = subprocess.run(["make"], cwd=str(SRC_DIR))
    if result.returncode == 0:
        print("✓ Agent compiled: keyclass_unwrapper")
    return result.returncode


def cmd_upload_agent(args: argparse.Namespace) -> int:
    if not AGENT.exists():
        print("✗ Agent not built yet. Run: keychain-decrypt build-agent")
        return 1
    port = getattr(args, "port", 2222)
    password = getattr(args, "password", "alpine")
    print(f"Uploading agent to device (port {port})...")
    cmd = [
        "sshpass", "-p", password,
        "scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no",
        f"-P{port}", str(AGENT), "root@localhost:",
    ]
    return subprocess.run(cmd).returncode


def cmd_download_db(args: argparse.Namespace) -> int:
    port = getattr(args, "port", 2222)
    password = getattr(args, "password", "alpine")
    print(f"Downloading keychain database (port {port})...")
    cmd = [
        "sshpass", "-p", password,
        "scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no",
        f"-P{port}", "root@localhost:/private/var/Keychains/keychain-2.db", ".",
    ]
    return subprocess.run(cmd, cwd=str(SRC_DIR)).returncode


def cmd_install_deps(args: argparse.Namespace) -> int:
    req = SRC_DIR / "requirements.txt"
    if not req.exists():
        print("✗ requirements.txt not found")
        return 1
    print("Installing keychain-decrypt dependencies...")
    return subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)]).returncode


def cmd_cleanup(args: argparse.Namespace) -> int:
    port = getattr(args, "port", 2222)
    password = getattr(args, "password", "alpine")
    print("Cleaning up device...")
    cmd = [
        "sshpass", "-p", password,
        "ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no",
        f"-p{port}", "root@localhost",
        "rm /var/root/keyclass_unwrapper; shutdown -h now",
    ]
    return subprocess.run(cmd).returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="keychain-decrypt",
        description="iOS Keychain Decrypter — Mobile Forensics for RECON",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"keychain-decrypt {VERSION}")

    sub = parser.add_subparsers(dest="command", title="subcommands")

    for name in ["decrypt", "upload-agent", "download-db", "cleanup"]:
        p = sub.add_parser(name)
        p.add_argument("--port", type=int, default=2222, help="SSH port (default: 2222)")
        p.add_argument("--password", default="alpine", help="SSH password (default: alpine)")

    sub.add_parser("build-agent", help="Compile the on-device agent")
    sub.add_parser("install-deps", help="Install Python dependencies")

    args = parser.parse_args()
    handlers = {
        "decrypt": cmd_decrypt, "build-agent": cmd_build_agent,
        "upload-agent": cmd_upload_agent, "download-db": cmd_download_db,
        "install-deps": cmd_install_deps, "cleanup": cmd_cleanup,
    }

    if not args.command:
        parser.print_help()
        sys.exit(0)

    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
