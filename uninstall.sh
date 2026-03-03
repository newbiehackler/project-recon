#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  PROJECT RECON — Uninstaller                                     ║
# ║  Cleanly removes Project RECON from this system.                 ║
# ║                                                                  ║
# ║  Usage: bash ~/RECON_WorkBench/uninstall.sh                      ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

RED='\033[1;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

INSTALL_DIR="$HOME/RECON_WorkBench"
RECON_DATA="$HOME/.recon"
BIN_DIR="$HOME/.local/bin"
PLIST="$HOME/Library/LaunchAgents/dev.recon.autoupdate.plist"

echo ""
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${BOLD}PROJECT RECON — Uninstaller${RESET}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

echo -e "${YELLOW}This will remove:${RESET}"
echo -e "  • $INSTALL_DIR"
echo -e "  • $RECON_DATA"
echo -e "  • CLI launchers in $BIN_DIR (recon, wmn, blackbird, cupidcr4wl, recon-update)"
echo -e "  • Auto-update launchd job"
echo -e "  • PATH entries from shell RC"
echo ""
echo -e "${BOLD}pip-installed OSINT tools and brew tools will NOT be removed.${RESET}"
echo ""
echo -n "Proceed? [y/N] "
read -r REPLY
if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""

# Remove auto-update launchd
if [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo -e "  ${GREEN}✓${RESET} Removed auto-update job"
fi

# Remove CLI launchers
for cmd in recon wmn blackbird cupidcr4wl recon-update; do
    if [ -f "$BIN_DIR/$cmd" ]; then
        rm -f "$BIN_DIR/$cmd"
        echo -e "  ${GREEN}✓${RESET} Removed $BIN_DIR/$cmd"
    fi
done

# Remove data directory
if [ -d "$RECON_DATA" ]; then
    echo -n "  Remove session/evidence data ($RECON_DATA)? [y/N] "
    read -r REPLY2
    if [[ "$REPLY2" =~ ^[Yy]$ ]]; then
        rm -rf "$RECON_DATA"
        echo -e "  ${GREEN}✓${RESET} Removed $RECON_DATA"
    else
        echo -e "  ${DIM}Kept $RECON_DATA${RESET}"
    fi
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "  ${GREEN}✓${RESET} Removed $INSTALL_DIR"
fi

# Clean shell RC
for RC in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile"; do
    if [ -f "$RC" ] && grep -qF '# ── Project RECON' "$RC" 2>/dev/null; then
        # Remove the RECON block (comment + 2 export lines)
        sed -i '' '/# ── Project RECON/,+2d' "$RC" 2>/dev/null || true
        echo -e "  ${GREEN}✓${RESET} Cleaned $RC"
    fi
done

echo ""
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${GREEN}${BOLD}Project RECON has been removed.${RESET}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${DIM}To also remove pip tools:${RESET}"
echo -e "  ${DIM}pip uninstall sherlock-project maigret social-analyzer socialscan holehe h8mail nexfil toutatis${RESET}"
echo ""
