.PHONY: install install-dev lint typecheck test smoke update bundle clean help

PYTHON ?= python3
PIP    ?= pip

# ── Default ──────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[31m%-15s\033[0m %s\n", $$1, $$2}'

# ── Installation ─────────────────────────────────────────────────
install: ## Install Project RECON (editable)
	$(PIP) install -e .

install-dev: ## Install with dev dependencies
	$(PIP) install -e ".[dev]"

install-all: ## Install with all optional dependencies
	$(PIP) install -e ".[all,dev]"

# ── Quality ──────────────────────────────────────────────────────
lint: ## Run ruff linter
	ruff check whatsmyname/

lint-fix: ## Run ruff with auto-fix
	ruff check --fix whatsmyname/

typecheck: ## Run mypy type checker
	mypy whatsmyname/ --ignore-missing-imports --no-strict-optional

# ── Testing ──────────────────────────────────────────────────────
test: ## Run pytest
	pytest tests/ -v

smoke: ## Quick smoke test (no external tools needed)
	recon --version
	recon --help
	recon --list-tools
	recon inventory
	recon categories
	recon templates
	@echo "\033[32m✓ All smoke tests passed\033[0m"

# ── Maintenance ──────────────────────────────────────────────────
update: ## Update all tools
	bash ../update.sh

# ── Bundle ───────────────────────────────────────────────────────
bundle: ## Create portable bundle in dist/
	@echo "Building portable bundle..."
	@mkdir -p dist/RECON_WorkBench
	@rsync -a --exclude='.DS_Store' --exclude='__pycache__' \
		--exclude='*.pyc' --exclude='*.egg-info' --exclude='.git' \
		--exclude='dist' --exclude='.venv' \
		../../RECON_WorkBench/ dist/RECON_WorkBench/
	@echo "Bundle size: $$(du -sh dist/RECON_WorkBench | awk '{print $$1}')"
	@echo "\033[32m✓ Bundle ready at dist/RECON_WorkBench/\033[0m"

# ── Cleanup ──────────────────────────────────────────────────────
clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info whatsmyname.egg-info/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
