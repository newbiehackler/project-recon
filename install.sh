#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  PROJECT RECON — Portable Installer v3.0.0                      ║
# ║  Rapid Evidence Collection & OSINT Network                      ║
# ║                                                                  ║
# ║  Usage:                                                          ║
# ║    bash /Volumes/YOUR_DRIVE/RECON_WorkBench/install.sh           ║
# ║                                                                  ║
# ║  What this does:                                                 ║
# ║    1. Copies Project RECON to ~/RECON_WorkBench                  ║
# ║    2. Creates a Python virtual environment                       ║
# ║    3. Installs all Python OSINT tools                            ║
# ║    4. Installs Homebrew + brew-based tools (optional)            ║
# ║    5. Adds 'recon' command to your PATH                         ║
# ║    6. Sets up auto-update (weekly via launchd)                   ║
# ║    7. Verifies everything works                                  ║
# ║                                                                  ║
# ║  Requirements: macOS 12+, Python 3.10+                          ║
# ║  Tested on: macOS Sonoma / Sequoia (Apple Silicon + Intel)      ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────
RED='\033[1;31m'
DRED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Globals ───────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/RECON_WorkBench"
VENV_DIR="$INSTALL_DIR/.venv"
RECON_DATA="$HOME/.recon"
BIN_DIR="$HOME/.local/bin"
LOG_FILE="/tmp/recon_install_$(date +%Y%m%d_%H%M%S).log"
ERRORS=0

# ── Helpers ───────────────────────────────────────────────────────
banner() {
    echo -e "${RED}"
    cat << 'EOF'
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ┃                                                       ┃
  ┃   ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗   ┃
  ┃   ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║   ┃
  ┃   ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║   ┃
  ┃   ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║   ┃
  ┃   ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║   ┃
  ┃   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ┃
  ┃                                                       ┃
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
    echo -e "${RESET}"
    echo -e "${DRED}  ┣━${RESET} ${BOLD}Rapid Evidence Collection & OSINT Network${RESET}"
    echo -e "${DRED}  ┣━${RESET} ${RED}☠ PROJECT RECON ☠${RESET}  ${DIM}v3.0.0 — Portable Installer${RESET}"
    echo -e "${DRED}  ┗━${RESET} ${DIM}█▓▒░${RESET} ${RED}ARMED${RESET} ${DIM}░▒▓█  // One Search · Every Tool · No Mercy //${RESET}"
    echo ""
}

step() {
    local num="$1"; shift
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${GREEN}  [${num}]${RESET} ${BOLD}$*${RESET}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

ok()   { echo -e "  ${GREEN}✓${RESET} $*"; }
warn() { echo -e "  ${YELLOW}⚠${RESET} $*"; }
fail() { echo -e "  ${RED}✗${RESET} $*"; ERRORS=$((ERRORS + 1)); }
info() { echo -e "  ${DIM}$*${RESET}"; }

log() { echo "[$(date '+%H:%M:%S')] $*" >> "$LOG_FILE"; }

require_cmd() {
    if ! command -v "$1" &>/dev/null; then
        fail "$1 not found. $2"
        return 1
    fi
    return 0
}

# ── Main ──────────────────────────────────────────────────────────
main() {
    banner
    log "=== PROJECT RECON installer started ==="
    log "Source: $SCRIPT_DIR"
    log "Target: $INSTALL_DIR"

    echo -e "  ${DIM}Source:${RESET}  $SCRIPT_DIR"
    echo -e "  ${DIM}Target:${RESET}  $INSTALL_DIR"
    echo -e "  ${DIM}Log:${RESET}    $LOG_FILE"
    echo ""

    # ────────────────────────────────────────────────────────────
    step "1/8" "Checking prerequisites"
    # ────────────────────────────────────────────────────────────

    if [[ "$(uname)" != "Darwin" ]]; then
        fail "This installer is for macOS only."
        exit 1
    fi
    ok "macOS $(sw_vers -productVersion) detected"

    if xcode-select -p &>/dev/null; then
        ok "Xcode Command Line Tools installed"
    else
        warn "Xcode CLT not found — installing (this may take a few minutes)..."
        xcode-select --install 2>/dev/null || true
        echo "  Press any key after Xcode CLT finishes installing..."
        read -r -n 1
    fi

    if ! require_cmd python3 "Install from https://www.python.org/downloads/"; then
        exit 1
    fi
    PY_VER=$(python3 -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}.{v.micro}")')
    PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    if [[ "$PY_MINOR" -lt 10 ]]; then
        fail "Python 3.10+ required (found $PY_VER)"
        exit 1
    fi
    ok "Python $PY_VER"

    if ! python3 -m pip --version &>/dev/null; then
        warn "pip not found — installing..."
        python3 -m ensurepip --upgrade >> "$LOG_FILE" 2>&1
    fi
    ok "pip $(python3 -m pip --version 2>/dev/null | awk '{print $2}')"

    if require_cmd git "Install via Xcode CLT or brew install git"; then
        ok "git $(git --version | awk '{print $3}')"
    fi

    # ────────────────────────────────────────────────────────────
    step "2/8" "Copying Project RECON"
    # ────────────────────────────────────────────────────────────

    if [ -d "$INSTALL_DIR" ]; then
        BACKUP="${INSTALL_DIR}.backup.$(date +%s)"
        warn "Existing installation found — backing up to $(basename "$BACKUP")"
        mv "$INSTALL_DIR" "$BACKUP"
        log "Backed up existing install to $BACKUP"
    fi

    rsync -a \
        --exclude='.DS_Store' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.egg-info' \
        "$SCRIPT_DIR/" "$INSTALL_DIR/"

    ok "Copied to $INSTALL_DIR"
    info "Size: $(du -sh "$INSTALL_DIR" | awk '{print $1}')"

    # ────────────────────────────────────────────────────────────
    step "3/8" "Creating Python virtual environment"
    # ────────────────────────────────────────────────────────────

    python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1
    ok "Virtual environment created at .venv/"
    info "Python: $(python --version)"

    # ────────────────────────────────────────────────────────────
    step "4/8" "Installing Project RECON + OSINT tools"
    # ────────────────────────────────────────────────────────────

    pip install -e "$INSTALL_DIR/WhatsMyName/" >> "$LOG_FILE" 2>&1
    ok "Project RECON core installed"

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
    )

    echo ""
    info "Installing ${#PIP_TOOLS[@]} OSINT tools..."
    INSTALLED_COUNT=0
    for tool in "${PIP_TOOLS[@]}"; do
        if pip install "$tool" >> "$LOG_FILE" 2>&1; then
            ok "$tool"
            INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
        else
            warn "$tool (install failed — see log)"
            log "WARN: $tool pip install failed"
        fi
    done
    echo ""
    ok "$INSTALLED_COUNT/${#PIP_TOOLS[@]} pip tools installed"

    # ────────────────────────────────────────────────────────────
    step "5/8" "Setting up launchers"
    # ────────────────────────────────────────────────────────────

    mkdir -p "$BIN_DIR"

    # Blackbird wrapper
    if [ -d "$INSTALL_DIR/tools/blackbird" ]; then
        cat > "$BIN_DIR/blackbird" << BEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/blackbird/blackbird.py" "\$@"
BEOF
        chmod +x "$BIN_DIR/blackbird"
        ok "blackbird → ~/.local/bin/blackbird"
    fi

    # Cupidcr4wl wrapper
    if [ -d "$INSTALL_DIR/tools/cupidcr4wl" ]; then
        cat > "$BIN_DIR/cupidcr4wl" << CEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/cupidcr4wl/cupidcr4wl.py" "\$@"
CEOF
        chmod +x "$BIN_DIR/cupidcr4wl"
        ok "cupidcr4wl → ~/.local/bin/cupidcr4wl"
    fi

    # CompreFace wrapper
    if [ -d "$INSTALL_DIR/tools/compreface" ]; then
        cat > "$BIN_DIR/compreface" << CFEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/compreface/compreface-cli.py" "\$@"
CFEOF
        chmod +x "$BIN_DIR/compreface"
        ok "compreface → ~/.local/bin/compreface"
    fi

    # untappdScraper wrapper
    if [ -d "$INSTALL_DIR/tools/untappd-scraper" ]; then
        # Install untappd deps
        pip install bs4 geocoder gmplot googlemaps requests >> "$LOG_FILE" 2>&1 || true
        cat > "$BIN_DIR/untappd-scraper" << UTEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/untappd-scraper/untappd-cli.py" "\$@"
UTEOF
        chmod +x "$BIN_DIR/untappd-scraper"
        ok "untappd-scraper → ~/.local/bin/untappd-scraper"
    fi

    # 4n6notebooks wrapper
    if [ -d "$INSTALL_DIR/tools/4n6notebooks" ]; then
        # Install 4n6notebooks deps
        if [ -f "$INSTALL_DIR/tools/4n6notebooks/src/requirements.txt" ]; then
            pip install -r "$INSTALL_DIR/tools/4n6notebooks/src/requirements.txt" >> "$LOG_FILE" 2>&1 || true
        fi
        cat > "$BIN_DIR/4n6notebooks" << NBEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/4n6notebooks/4n6notebooks-cli.py" "\$@"
NBEOF
        chmod +x "$BIN_DIR/4n6notebooks"
        ok "4n6notebooks → ~/.local/bin/4n6notebooks"
    fi

    # iOS Keychain Decrypter wrapper
    if [ -d "$INSTALL_DIR/tools/keychain-decrypter" ]; then
        # Install keychain deps
        if [ -f "$INSTALL_DIR/tools/keychain-decrypter/src/requirements.txt" ]; then
            pip install -r "$INSTALL_DIR/tools/keychain-decrypter/src/requirements.txt" >> "$LOG_FILE" 2>&1 || true
        fi
        # Build agent if Xcode is available
        if [ -f "$INSTALL_DIR/tools/keychain-decrypter/src/Makefile" ] && xcode-select -p &>/dev/null; then
            info "Building keychain agent..."
            make -C "$INSTALL_DIR/tools/keychain-decrypter/src" >> "$LOG_FILE" 2>&1 || warn "keychain agent build failed (Xcode signing may be needed)"
        fi
        cat > "$BIN_DIR/keychain-decrypt" << KCEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/keychain-decrypter/keychain-cli.py" "\$@"
KCEOF
        chmod +x "$BIN_DIR/keychain-decrypt"
        ok "keychain-decrypt → ~/.local/bin/keychain-decrypt"
    fi

    # OSINT Tools CLI wrapper (Rust TUI)
    if [ -d "$INSTALL_DIR/tools/osint-tools-cli" ]; then
        # Build if cargo is available
        if command -v cargo &>/dev/null && [ -f "$INSTALL_DIR/tools/osint-tools-cli/src/Cargo.toml" ]; then
            info "Building osint-tools-cli (Rust)..."
            cargo build --release --manifest-path "$INSTALL_DIR/tools/osint-tools-cli/src/Cargo.toml" >> "$LOG_FILE" 2>&1 && ok "osint-tools-cli compiled" || warn "osint-tools-cli build failed (install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh)"
        fi
        cat > "$BIN_DIR/osint-tools-cli" << OTEOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/tools/osint-tools-cli/osint-tools-cli-wrapper.py" "\$@"
OTEOF
        chmod +x "$BIN_DIR/osint-tools-cli"
        ok "osint-tools-cli → ~/.local/bin/osint-tools-cli"
    fi

    # Main recon launcher (activates venv automatically)
    cat > "$BIN_DIR/recon" << 'REOF'
#!/usr/bin/env bash
# Project RECON — CLI launcher
RECON_HOME="$HOME/RECON_WorkBench"
VENV="$RECON_HOME/.venv/bin/activate"
[ -f "$VENV" ] && source "$VENV"
exec python3 -m whatsmyname.recon_cli "$@"
REOF
    chmod +x "$BIN_DIR/recon"
    ok "recon → ~/.local/bin/recon"

    # WMN launcher
    cat > "$BIN_DIR/wmn" << 'WEOF'
#!/usr/bin/env bash
RECON_HOME="$HOME/RECON_WorkBench"
VENV="$RECON_HOME/.venv/bin/activate"
[ -f "$VENV" ] && source "$VENV"
exec python3 -m whatsmyname.cli "$@"
WEOF
    chmod +x "$BIN_DIR/wmn"
    ok "wmn → ~/.local/bin/wmn"

    # ────────────────────────────────────────────────────────────
    step "6/8" "Configuring shell"
    # ────────────────────────────────────────────────────────────

    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi

    if [ -n "$SHELL_RC" ]; then
        if ! grep -qF '# ── Project RECON' "$SHELL_RC" 2>/dev/null; then
            {
                echo ""
                echo "# ── Project RECON ──────────────────────────────"
                echo 'export PATH="$HOME/.local/bin:$PATH"'
                echo 'export RECON_HOME="$HOME/RECON_WorkBench"'
            } >> "$SHELL_RC"
            ok "Added to $SHELL_RC"
        else
            ok "Already configured in $SHELL_RC"
        fi
    else
        warn "No shell RC file found — add manually:"
        echo '    export PATH="$HOME/.local/bin:$PATH"'
        echo '    export RECON_HOME="$HOME/RECON_WorkBench"'
    fi

    export PATH="$BIN_DIR:$PATH"
    export RECON_HOME="$INSTALL_DIR"

    # ────────────────────────────────────────────────────────────
    step "7/8" "Homebrew tools (optional)"
    # ────────────────────────────────────────────────────────────

    BREW_TOOLS=(
        nmap wireshark exiftool testdisk john-jumbo steghide binwalk
        foremost hashcat yara sleuthkit bulk_extractor radare2
        aircrack-ng hydra sqlmap
    )

    if command -v brew &>/dev/null; then
        ok "Homebrew found"
        echo ""
        echo -e "  ${BOLD}${#BREW_TOOLS[@]} forensics tools available:${RESET}"
        echo -e "  ${DIM}${BREW_TOOLS[*]}${RESET}"
        echo ""
        echo -n "  Install brew tools now? [Y/n] "
        read -r REPLY
        if [[ -z "$REPLY" || "$REPLY" =~ ^[Yy]$ ]]; then
            for tool in "${BREW_TOOLS[@]}"; do
                if brew list "$tool" &>/dev/null 2>&1; then
                    ok "$tool (already installed)"
                else
                    info "Installing $tool..."
                    if brew install "$tool" >> "$LOG_FILE" 2>&1; then
                        ok "$tool"
                    else
                        warn "$tool (brew install failed)"
                    fi
                fi
            done
        else
            info "Skipped — run 'recon update --brew' later to install"
        fi
    else
        warn "Homebrew not found"
        echo -e "  ${DIM}Install: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${RESET}"
        echo -e "  ${DIM}Then run: recon update --brew${RESET}"
    fi

    # ────────────────────────────────────────────────────────────
    step "8/8" "Workspace & auto-update"
    # ────────────────────────────────────────────────────────────

    mkdir -p "$RECON_DATA"/{plugins,sessions,spotlight_plugins,evidence,exports,logs}
    ok "Data directory: $RECON_DATA"

    # Copy update script to bin
    if [ -f "$INSTALL_DIR/update.sh" ]; then
        cp "$INSTALL_DIR/update.sh" "$BIN_DIR/recon-update"
        chmod +x "$BIN_DIR/recon-update"
        ok "Update script installed"
    fi

    # Weekly auto-update via launchd
    PLIST_DIR="$HOME/Library/LaunchAgents"
    PLIST_FILE="$PLIST_DIR/dev.recon.autoupdate.plist"
    mkdir -p "$PLIST_DIR"

    cat > "$PLIST_FILE" << PEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>dev.recon.autoupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>${BIN_DIR}/recon-update</string>
        <string>--auto</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${RECON_DATA}/logs/autoupdate.log</string>
    <key>StandardErrorPath</key>
    <string>${RECON_DATA}/logs/autoupdate_err.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PEOF

    launchctl load "$PLIST_FILE" 2>/dev/null || true
    ok "Auto-update: weekly (Monday 3:00 AM)"

    # ────────────────────────────────────────────────────────────
    # Verification
    # ────────────────────────────────────────────────────────────

    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "  ${BOLD}Verification${RESET}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

    if "$BIN_DIR/recon" --version &>/dev/null; then
        RECON_VER=$("$BIN_DIR/recon" --version 2>&1)
        ok "recon works: $RECON_VER"
    else
        fail "recon command failed — check $LOG_FILE"
    fi

    # ────────────────────────────────────────────────────────────
    # Done
    # ────────────────────────────────────────────────────────────

    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}☠ PROJECT RECON — INSTALLATION COMPLETE ☠${RESET}"
    else
        echo -e "  ${YELLOW}${BOLD}☠ PROJECT RECON — INSTALLED WITH $ERRORS WARNING(S) ☠${RESET}"
    fi
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
    echo -e "  ${BOLD}Open a new terminal${RESET}, then:"
    echo ""
    echo -e "  ${GREEN}recon --help${RESET}              Full command reference"
    echo -e "  ${GREEN}recon --version${RESET}           Verify installation"
    echo -e "  ${GREEN}recon inventory${RESET}           See all installed tools"
    echo -e "  ${GREEN}recon johndoe${RESET}             Search a username"
    echo -e "  ${GREEN}recon shell${RESET}               Interactive REPL"
    echo -e "  ${GREEN}recon update${RESET}              Update all tools"
    echo ""
    echo -e "  ${DIM}Location:${RESET}     $INSTALL_DIR"
    echo -e "  ${DIM}Data:${RESET}         $RECON_DATA"
    echo -e "  ${DIM}Log:${RESET}          $LOG_FILE"
    echo -e "  ${DIM}Auto-update:${RESET}  Every Monday @ 3:00 AM"
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
}

main "$@"
