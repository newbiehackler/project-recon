"""
RECON Sessions — persistent investigation tracking across runs.

Sessions store: targets searched, tools run, findings, timestamps, notes.
Stored as JSON in ~/.recon/sessions/<name>.json
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSION_DIR = Path.home() / ".recon" / "sessions"


def ensure_session_dir() -> Path:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR


@dataclass
class SessionRun:
    """A single execution within a session."""
    timestamp: str
    target: str
    input_type: str
    tools_run: list[str] = field(default_factory=list)
    findings_count: int = 0
    categories_found: list[str] = field(default_factory=list)
    elapsed: float = 0.0
    notes: str = ""
    case_id: str = ""


@dataclass
class Session:
    """A persistent investigation session."""
    name: str
    created: str = ""
    updated: str = ""
    runs: list[SessionRun] = field(default_factory=list)
    all_targets: list[str] = field(default_factory=list)
    all_findings: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    case_id: str = ""
    examiner: str = ""

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now(timezone.utc).isoformat()
        if not self.updated:
            self.updated = self.created

    def add_run(self, run: SessionRun) -> None:
        self.runs.append(run)
        if run.target not in self.all_targets:
            self.all_targets.append(run.target)
        self.updated = datetime.now(timezone.utc).isoformat()

    def add_findings(self, findings: list[dict]) -> None:
        self.all_findings.extend(findings)
        self.updated = datetime.now(timezone.utc).isoformat()

    def add_note(self, note: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.notes.append(f"[{ts}] {note}")
        self.updated = datetime.now(timezone.utc).isoformat()

    @property
    def total_findings(self) -> int:
        return len(self.all_findings)

    @property
    def total_runs(self) -> int:
        return len(self.runs)

    @property
    def unique_targets(self) -> list[str]:
        return list(dict.fromkeys(self.all_targets))

    @property
    def unique_tools_used(self) -> list[str]:
        tools = []
        for run in self.runs:
            for t in run.tools_run:
                if t not in tools:
                    tools.append(t)
        return tools

    def summary(self) -> dict:
        return {
            "name": self.name,
            "created": self.created,
            "updated": self.updated,
            "total_runs": self.total_runs,
            "total_findings": self.total_findings,
            "targets": self.unique_targets,
            "tools_used": self.unique_tools_used,
            "case_id": self.case_id,
            "examiner": self.examiner,
        }


def _session_path(name: str) -> Path:
    ensure_session_dir()
    # Sanitize name for filesystem
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    return SESSION_DIR / f"{safe_name}.json"


def save_session(session: Session) -> Path:
    """Save session to disk."""
    path = _session_path(session.name)
    data = {
        "name": session.name,
        "created": session.created,
        "updated": session.updated,
        "case_id": session.case_id,
        "examiner": session.examiner,
        "notes": session.notes,
        "all_targets": session.all_targets,
        "runs": [asdict(r) for r in session.runs],
        "all_findings": session.all_findings,
    }
    path.write_text(json.dumps(data, indent=2, default=str))
    return path


def load_session(name: str) -> Session | None:
    """Load a session from disk."""
    path = _session_path(name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        session = Session(
            name=data["name"],
            created=data.get("created", ""),
            updated=data.get("updated", ""),
            case_id=data.get("case_id", ""),
            examiner=data.get("examiner", ""),
            notes=data.get("notes", []),
            all_targets=data.get("all_targets", []),
            all_findings=data.get("all_findings", []),
        )
        for run_data in data.get("runs", []):
            session.runs.append(SessionRun(**run_data))
        return session
    except Exception:
        return None


def list_sessions() -> list[dict]:
    """List all saved sessions with summaries."""
    ensure_session_dir()
    sessions = []
    for path in sorted(SESSION_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
            sessions.append({
                "name": data.get("name", path.stem),
                "created": data.get("created", ""),
                "updated": data.get("updated", ""),
                "runs": len(data.get("runs", [])),
                "targets": len(data.get("all_targets", [])),
                "findings": len(data.get("all_findings", [])),
                "case_id": data.get("case_id", ""),
                "path": str(path),
            })
        except Exception:
            pass
    return sessions


def delete_session(name: str) -> bool:
    """Delete a session file."""
    path = _session_path(name)
    if path.exists():
        path.unlink()
        return True
    return False


def create_or_resume(name: str) -> Session:
    """Create a new session or resume an existing one."""
    existing = load_session(name)
    if existing:
        return existing
    return Session(name=name)
