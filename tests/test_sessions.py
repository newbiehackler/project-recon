"""Tests for whatsmyname.sessions — session tracking and persistence."""

import json
from pathlib import Path

from whatsmyname.sessions import (
    Session,
    SessionRun,
    create_or_resume,
    delete_session,
    load_session,
    save_session,
)


class TestSessionRun:
    def test_defaults(self):
        run = SessionRun(timestamp="2026-01-01T00:00:00Z", target="johndoe", input_type="username")
        assert run.findings_count == 0
        assert run.tools_run == []
        assert run.elapsed == 0.0


class TestSession:
    def test_init_sets_timestamps(self):
        s = Session(name="test")
        assert s.created != ""
        assert s.updated != ""

    def test_add_run(self):
        s = Session(name="test")
        run = SessionRun(timestamp="2026-01-01T00:00:00Z", target="johndoe", input_type="username")
        s.add_run(run)
        assert s.total_runs == 1
        assert "johndoe" in s.all_targets

    def test_add_run_no_duplicate_targets(self):
        s = Session(name="test")
        r1 = SessionRun(timestamp="t1", target="johndoe", input_type="username")
        r2 = SessionRun(timestamp="t2", target="johndoe", input_type="username")
        s.add_run(r1)
        s.add_run(r2)
        assert s.total_runs == 2
        assert s.all_targets.count("johndoe") == 1

    def test_add_findings(self):
        s = Session(name="test")
        s.add_findings([{"url": "https://example.com", "site_name": "Example"}])
        assert s.total_findings == 1

    def test_add_note(self):
        s = Session(name="test")
        s.add_note("found something interesting")
        assert len(s.notes) == 1
        assert "found something interesting" in s.notes[0]

    def test_unique_tools_used(self):
        s = Session(name="test")
        r1 = SessionRun(timestamp="t1", target="a", input_type="username", tools_run=["wmn", "sherlock"])
        r2 = SessionRun(timestamp="t2", target="b", input_type="username", tools_run=["wmn", "maigret"])
        s.add_run(r1)
        s.add_run(r2)
        tools = s.unique_tools_used
        assert "wmn" in tools
        assert "sherlock" in tools
        assert "maigret" in tools
        assert tools.count("wmn") == 1

    def test_summary(self):
        s = Session(name="test", case_id="CASE-001", examiner="analyst")
        summary = s.summary()
        assert summary["name"] == "test"
        assert summary["case_id"] == "CASE-001"


class TestSessionPersistence:
    def test_save_and_load(self, tmp_path, monkeypatch):
        # Redirect session dir to tmp
        monkeypatch.setattr("whatsmyname.sessions.SESSION_DIR", tmp_path)

        s = Session(name="test-persist")
        s.add_note("hello")
        run = SessionRun(timestamp="t1", target="johndoe", input_type="username", tools_run=["wmn"])
        s.add_run(run)
        save_session(s)

        loaded = load_session("test-persist")
        assert loaded is not None
        assert loaded.name == "test-persist"
        assert loaded.total_runs == 1
        assert len(loaded.notes) == 1

    def test_load_nonexistent(self, tmp_path, monkeypatch):
        monkeypatch.setattr("whatsmyname.sessions.SESSION_DIR", tmp_path)
        assert load_session("nonexistent") is None

    def test_create_or_resume_new(self, tmp_path, monkeypatch):
        monkeypatch.setattr("whatsmyname.sessions.SESSION_DIR", tmp_path)
        s = create_or_resume("brand-new")
        assert s.name == "brand-new"
        assert s.total_runs == 0

    def test_create_or_resume_existing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("whatsmyname.sessions.SESSION_DIR", tmp_path)
        s = Session(name="existing")
        s.add_note("prior note")
        save_session(s)

        resumed = create_or_resume("existing")
        assert len(resumed.notes) == 1

    def test_delete_session(self, tmp_path, monkeypatch):
        monkeypatch.setattr("whatsmyname.sessions.SESSION_DIR", tmp_path)
        s = Session(name="to-delete")
        save_session(s)
        assert delete_session("to-delete") is True
        assert delete_session("to-delete") is False
