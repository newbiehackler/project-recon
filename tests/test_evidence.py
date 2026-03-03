"""Tests for whatsmyname.evidence — evidence bag, hashing, chain of custody."""

import json

from whatsmyname.evidence import EvidenceBag


class TestEvidenceBagHashing:
    def test_hash_string_deterministic(self):
        h1 = EvidenceBag.hash_string("hello world")
        h2 = EvidenceBag.hash_string("hello world")
        assert h1 == h2

    def test_hash_string_changes_with_input(self):
        h1 = EvidenceBag.hash_string("hello")
        h2 = EvidenceBag.hash_string("world")
        assert h1 != h2

    def test_hash_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("test content")
        h = EvidenceBag.hash_file(f)
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex length


class TestEvidenceBagStorage:
    def test_store_artifact_text(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        path = bag.store_artifact("test.txt", "hello", artifact_type="output", tool_name="wmn")
        assert path.exists()
        assert path.read_text() == "hello"

    def test_store_artifact_bytes(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        path = bag.store_artifact("test.bin", b"\x00\x01\x02", artifact_type="output")
        assert path.exists()
        assert path.read_bytes() == b"\x00\x01\x02"

    def test_manifest_populated(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        bag.store_artifact("a.txt", "aaa", tool_name="tool1")
        bag.store_artifact("b.txt", "bbb", tool_name="tool2")
        assert len(bag.manifest) == 2
        assert bag.manifest[0]["filename"] == "a.txt"
        assert bag.manifest[1]["filename"] == "b.txt"

    def test_chain_of_custody_logged(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"), case_id="CASE-1", examiner="tester")
        bag.store_artifact("a.txt", "data")
        # At least 2 chain entries: creation + artifact_stored
        assert len(bag.chain) >= 2
        actions = [e["action"] for e in bag.chain]
        assert "evidence_bag_created" in actions
        assert "artifact_stored" in actions

    def test_verify_integrity_passes(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        bag.store_artifact("a.txt", "data")
        failures = bag.verify_integrity()
        assert failures == []

    def test_verify_integrity_detects_tampering(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        path = bag.store_artifact("a.txt", "original")
        # Tamper with the file
        path.write_text("tampered")
        failures = bag.verify_integrity()
        assert len(failures) == 1
        assert failures[0]["error"] == "hash mismatch"

    def test_finalize_writes_manifest_and_chain(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"), case_id="C1")
        bag.store_artifact("report.json", '{"key": "value"}', tool_name="recon")
        manifest_path = bag.finalize()

        assert manifest_path.exists()
        assert (tmp_path / "evidence" / "CHAIN_OF_CUSTODY.json").exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["case_id"] == "C1"
        assert len(manifest["artifacts"]) == 1

    def test_store_raw_output(self, tmp_path):
        bag = EvidenceBag(str(tmp_path / "evidence"))
        stdout_path, stderr_path = bag.store_raw_output("sherlock", "found: 5 sites", "")
        assert stdout_path is not None
        assert stderr_path is None  # empty stderr not stored
