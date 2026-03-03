"""
RECON Evidence Module — chain of custody logging, hashing, and evidence bag.

Provides forensically sound output with:
- SHA-256 hashes of all artifacts
- Timestamped action log (chain of custody)
- Evidence bag directory with manifest
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


class EvidenceBag:
    """
    Creates a forensically sound evidence bag directory with:
    - All tool outputs
    - SHA-256 hash manifest
    - Chain of custody log
    """

    def __init__(self, base_dir: str, case_id: str = "", examiner: str = ""):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.case_id = case_id
        self.examiner = examiner
        self.manifest: list[dict] = []
        self.chain: list[dict] = []

        # Log creation
        self._log_action("evidence_bag_created", {
            "path": str(self.base_dir),
            "case_id": case_id,
            "examiner": examiner,
        })

    def _log_action(self, action: str, details: dict | None = None) -> None:
        """Add an entry to the chain of custody log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "examiner": self.examiner,
            "details": details or {},
        }
        self.chain.append(entry)

    @staticmethod
    def hash_file(path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def hash_string(data: str) -> str:
        """Compute SHA-256 hash of a string."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def store_artifact(
        self,
        filename: str,
        content: str | bytes,
        artifact_type: str = "output",
        tool_name: str = "",
    ) -> Path:
        """
        Store an artifact in the evidence bag with hash verification.
        Returns the path to the stored file.
        """
        # Create subdirectory by type
        subdir = self.base_dir / artifact_type
        subdir.mkdir(exist_ok=True)

        filepath = subdir / filename
        if isinstance(content, str):
            filepath.write_text(content)
        else:
            filepath.write_bytes(content)

        file_hash = self.hash_file(filepath)

        entry = {
            "filename": filename,
            "path": str(filepath.relative_to(self.base_dir)),
            "type": artifact_type,
            "tool": tool_name,
            "sha256": file_hash,
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.manifest.append(entry)

        self._log_action("artifact_stored", {
            "filename": filename,
            "sha256": file_hash,
            "tool": tool_name,
        })

        return filepath

    def store_raw_output(
        self, tool_name: str, stdout: str, stderr: str
    ) -> tuple[Path | None, Path | None]:
        """Store raw stdout/stderr from a tool run."""
        stdout_path = None
        stderr_path = None

        if stdout.strip():
            stdout_path = self.store_artifact(
                f"{tool_name}_stdout.txt", stdout,
                artifact_type="raw_output", tool_name=tool_name,
            )
        if stderr.strip():
            stderr_path = self.store_artifact(
                f"{tool_name}_stderr.txt", stderr,
                artifact_type="raw_output", tool_name=tool_name,
            )

        return stdout_path, stderr_path

    def store_report(self, filename: str, content: str) -> Path:
        """Store a report in the evidence bag."""
        return self.store_artifact(
            filename, content, artifact_type="reports", tool_name="recon",
        )

    def verify_integrity(self) -> list[dict]:
        """
        Verify all stored artifacts against their recorded hashes.
        Returns list of any failures.
        """
        failures = []
        for entry in self.manifest:
            filepath = self.base_dir / entry["path"]
            if not filepath.exists():
                failures.append({
                    "file": entry["filename"],
                    "error": "file missing",
                    "expected_hash": entry["sha256"],
                })
                continue

            current_hash = self.hash_file(filepath)
            if current_hash != entry["sha256"]:
                failures.append({
                    "file": entry["filename"],
                    "error": "hash mismatch",
                    "expected_hash": entry["sha256"],
                    "actual_hash": current_hash,
                })

        self._log_action("integrity_check", {
            "total_files": len(self.manifest),
            "failures": len(failures),
        })

        return failures

    def finalize(self) -> Path:
        """
        Write the manifest and chain of custody to the evidence bag.
        Returns path to the manifest file.
        """
        self._log_action("evidence_bag_finalized", {
            "total_artifacts": len(self.manifest),
            "total_chain_entries": len(self.chain),
        })

        # Write manifest
        manifest_data = {
            "case_id": self.case_id,
            "examiner": self.examiner,
            "created": self.chain[0]["timestamp"] if self.chain else "",
            "finalized": datetime.now(timezone.utc).isoformat(),
            "artifacts": self.manifest,
        }
        manifest_path = self.base_dir / "MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest_data, indent=2))

        # Hash the manifest itself
        manifest_hash = self.hash_file(manifest_path)

        # Write chain of custody
        chain_data = {
            "case_id": self.case_id,
            "examiner": self.examiner,
            "manifest_sha256": manifest_hash,
            "entries": self.chain,
        }
        chain_path = self.base_dir / "CHAIN_OF_CUSTODY.json"
        chain_path.write_text(json.dumps(chain_data, indent=2))

        # Write human-readable summary
        summary_lines = [
            "RECON Evidence Bag",
            "==================",
            f"Case ID:    {self.case_id or 'N/A'}",
            f"Examiner:   {self.examiner or 'N/A'}",
            f"Created:    {self.chain[0]['timestamp'] if self.chain else 'N/A'}",
            f"Finalized:  {datetime.now(timezone.utc).isoformat()}",
            "",
            f"Artifacts:  {len(self.manifest)}",
            f"Chain entries: {len(self.chain)}",
            "",
            f"Manifest SHA-256: {manifest_hash}",
            "",
            "Files:",
        ]
        for entry in self.manifest:
            summary_lines.append(
                f"  {entry['sha256'][:16]}...  {entry['path']}  ({entry['size_bytes']} bytes)"
            )

        readme_path = self.base_dir / "README.txt"
        readme_path.write_text("\n".join(summary_lines))

        return manifest_path
