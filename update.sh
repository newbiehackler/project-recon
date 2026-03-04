#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  PROJECT RECON — Updater v3.0.0                                  ║
# ║  Updates all OSINT tools, dependencies, and RECON itself.        ║
# ║                                                                  ║
# ║  Usage:                                                          ║
# ║    recon-update              # Update everything                 ║
# ║    recon-update --pip        # Only pip tools                    ║
# ║    recon-update --brew       # Only brew tools                   ║
# ║    recon-update --bundled    # Only bundled tools (git repos)    ║
# ║    recon-update --auto       # Silent mode (for launchd)         ║
# ╚══════════════════════════════════════════════════════════════════╝

set -uo pipefail

# ── Colors ────────────────────────────────────────────────────────
RED='\033[1;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Globals ───────────────────────────────────────────────────────
INSTALL_DIR="${RECON_HOME:-$HOME/RECON_WorkBench}"
VENV_DIR="$INSTALL_DIR/.venv"
RECON_DATA="$HOME/.recon"
LOG_FILE="$RECON_DATA/logs/update_$(date +%Y%m%d_%H%M%S).log"
AUTO_MODE=false
DO_PIP=true
DO_BREW=true
DO_BUNDLED=true
UPDATED=0
FAILED=0

# ── Parse args ────────────────────────────────────────────────────
for arg in "$@"; do
    case "$arg" in
        --auto)     AUTO_MODE=true ;;
        --pip)      DO_BREW=false; DO_BUNDLED=false ;;
        --brew)     DO_PIP=false; DO_BUNDLED=false ;;
        --bundled)  DO_PIP=false; DO_BREW=false ;;
        --help|-h)
            echo "Usage: recon-update [--pip|--brew|--bundled|--auto]"
            exit 0
            ;;
    esac
done

# ── Helpers ───────────────────────────────────────────────────────
ok()   { $AUTO_MODE || echo -e "  ${GREEN}✓${RESET} $*"; }
warn() { $AUTO_MODE || echo -e "  ${YELLOW}⚠${RESET} $*"; }
fail() { $AUTO_MODE || echo -e "  ${RED}✗${RESET} $*"; FAILED=$((FAILED + 1)); }
info() { $AUTO_MODE || echo -e "  ${DIM}$*${RESET}"; }

log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

step() {
    $AUTO_MODE && return
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "  ${BOLD}$*${RESET}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

# ── Activate venv ─────────────────────────────────────────────────
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "ERROR: Virtual environment not found at $VENV_DIR"
    echo "Run the installer first: bash ~/RECON_WorkBench/install.sh"
    exit 1
fi

log "=== RECON update started ==="

if ! $AUTO_MODE; then
    echo ""
    echo -e "${RED}☠ PROJECT RECON${RESET} — ${BOLD}Updater${RESET}"
    echo ""
fi

# ── 1. pip tools ──────────────────────────────────────────────────
if $DO_PIP; then
    step "Updating Python tools"

    # Upgrade pip itself
    pip install --upgrade pip >> "$LOG_FILE" 2>&1 && ok "pip" || warn "pip"

    # Core RECON package
    pip install --upgrade -e "$INSTALL_DIR/WhatsMyName/" >> "$LOG_FILE" 2>&1 && \
        ok "project-recon (core)" || fail "project-recon (core)"

    PIP_TOOLS=(
        "sherlock-project"
        "maigret"
        "social-analyzer"
        "socialscan"
        "holehe"
        "h8mail"
        "nexfil"
        "toutatis"
        "volatility3"
        "oletools"
        "stegoveritas"
        "scapy"
        "rich"
        "aiohttp"
        "aiohttp-socks"
    )

    for tool in "${PIP_TOOLS[@]}"; do
        if pip install --upgrade "$tool" >> "$LOG_FILE" 2>&1; then
            ok "$tool"
            UPDATED=$((UPDATED + 1))
        else
            warn "$tool (upgrade failed)"
            log "WARN: $tool upgrade failed"
        fi
    done
fi

# ── 2. Bundled tools (git repos) ─────────────────────────────────
if $DO_BUNDLED; then
    step "Updating bundled tools"

    for repo_dir in "$INSTALL_DIR/tools"/*/; do
        [ -d "$repo_dir/.git" ] || continue
        repo_name=$(basename "$repo_dir")
        if git -C "$repo_dir" pull --ff-only >> "$LOG_FILE" 2>&1; then
            ok "$repo_name (git pull)"
            UPDATED=$((UPDATED + 1))
        else
            warn "$repo_name (git pull failed — may need manual update)"
            log "WARN: git pull failed for $repo_name"
        fi
    done

    # Install/update requirements for bundled tools
    for repo_dir in "$INSTALL_DIR/tools"/*/; do
        repo_name=$(basename "$repo_dir")
        # Check top-level and src/ subdirectory for requirements
        for req in "$repo_dir/requirements.txt" "$repo_dir/src/requirements.txt"; do
            if [ -f "$req" ]; then
                pip install --upgrade -r "$req" >> "$LOG_FILE" 2>&1 && \
                    ok "$repo_name deps" || warn "$repo_name deps"
                break
            fi
        done
    done

    # Rebuild Rust tools (osint-tools-cli)
    if command -v cargo &>/dev/null && [ -f "$INSTALL_DIR/tools/osint-tools-cli/src/Cargo.toml" ]; then
        info "Rebuilding osint-tools-cli..."
        cargo build --release --manifest-path "$INSTALL_DIR/tools/osint-tools-cli/src/Cargo.toml" >> "$LOG_FILE" 2>&1 && \
            ok "osint-tools-cli rebuilt" || warn "osint-tools-cli rebuild failed"
    fi

    # Rebuild keychain agent (if Xcode available)
    if [ -f "$INSTALL_DIR/tools/keychain-decrypter/src/Makefile" ] && xcode-select -p &>/dev/null; then
        info "Rebuilding keychain agent..."
        make -C "$INSTALL_DIR/tools/keychain-decrypter/src" >> "$LOG_FILE" 2>&1 && \
            ok "keychain agent rebuilt" || warn "keychain agent rebuild failed"
    fi
fi

# ── 3. Brew tools ────────────────────────────────────────────────
if $DO_BREW; then
    step "Updating Homebrew tools"

    if command -v brew &>/dev/null; then
        info "Running brew update..."
        brew update >> "$LOG_FILE" 2>&1 && ok "brew update" || warn "brew update"

        BREW_TOOLS=(
            nmap wireshark exiftool testdisk john-jumbo steghide binwalk
            foremost hashcat yara sleuthkit bulk_extractor radare2
            aircrack-ng hydra sqlmap
        )

        for tool in "${BREW_TOOLS[@]}"; do
            if brew list "$tool" &>/dev/null 2>&1; then
                if brew upgrade "$tool" >> "$LOG_FILE" 2>&1; then
                    ok "$tool"
                    UPDATED=$((UPDATED + 1))
                else
                    # brew upgrade returns non-zero if already up to date
                    ok "$tool (up to date)"
                fi
            else
                info "$tool not installed — installing..."
                if brew install "$tool" >> "$LOG_FILE" 2>&1; then
                    ok "$tool (newly installed)"
                    UPDATED=$((UPDATED + 1))
                else
                    warn "$tool (install failed)"
                fi
            fi
        done
    else
        warn "Homebrew not found — skipping brew tools"
    fi
fi

# ── 4. Update WMN data ──────────────────────────────────────────
step "Updating WMN site data"
if command -v wmn &>/dev/null; then
    wmn --update >> "$LOG_FILE" 2>&1 && ok "WMN data refreshed" || warn "WMN data update failed"
else
    info "wmn not in PATH — skipping data update"
fi

# ── Summary ──────────────────────────────────────────────────────
log "Update complete: $UPDATED updated, $FAILED failed"

if ! $AUTO_MODE; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    if [ "$FAILED" -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}☠ UPDATE COMPLETE${RESET} — $UPDATED components updated"
    else
        echo -e "  ${YELLOW}${BOLD}☠ UPDATE COMPLETE${RESET} — $UPDATED updated, ${RED}$FAILED failed${RESET}"
    fi
    echo -e "  ${DIM}Log: $LOG_FILE${RESET}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
fi
