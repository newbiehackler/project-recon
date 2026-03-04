#!/usr/bin/env python3
"""
CompreFace CLI — RECON Face Recognition & Image Intelligence Wrapper

Provides a unified CLI interface to the CompreFace Docker-based face
recognition service. Manages the service lifecycle and exposes the
REST API through simple subcommands.

Part of Project RECON — Rapid Evidence Collection & OSINT Network
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOOL_DIR = Path(__file__).resolve().parent
COMPOSE_FILE = TOOL_DIR / "docker-compose.yml"
ENV_FILE = TOOL_DIR / "CompreFace" / ".env"
DEFAULT_API_URL = "http://localhost:8000"
VERSION = "1.0.0"

BANNER = r"""
   ██████╗ ██████╗ ███╗   ███╗██████╗ ██████╗ ███████╗
  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔════╝
  ██║     ██║   ██║██╔████╔██║██████╔╝██████╔╝█████╗
  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══██╗██╔══╝
  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║███████╗
   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝
  Face Recognition & Image Intelligence — RECON Module
"""

HELP_EPILOG = textwrap.dedent("""\

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     COMPREFACE — Face Recognition & Image Intelligence for RECON
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    OVERVIEW
    ────────
      CompreFace is a self-hosted face recognition service powered by
      deep learning. It runs as a set of Docker containers and exposes
      a REST API for face detection, recognition, verification, and
      landmark extraction.

      This CLI wrapper manages the Docker service lifecycle and provides
      convenient command-line access to all API operations.

    ARCHITECTURE
    ────────────
      CompreFace runs 5 Docker containers:
        • compreface-core         ML engine (face detection & embeddings)
        • compreface-api          REST API gateway
        • compreface-admin        Admin panel & API key management
        • compreface-fe           Web UI (http://localhost:8000)
        • compreface-postgres-db  PostgreSQL database

    FIRST-TIME SETUP
    ────────────────
      1. Start the service:
           compreface start

      2. Open the web UI:
           open http://localhost:8000

      3. Create an application and get an API key from the admin panel

      4. Set your API key:
           export COMPREFACE_API_KEY="your-api-key-here"

      5. Add subjects (known faces) via the web UI or API:
           compreface add-subject --name "John Doe" --image photo.jpg

    SUBCOMMANDS
    ───────────
      Service Management:
        start                Start CompreFace Docker containers
        stop                 Stop CompreFace Docker containers
        restart              Restart all containers
        status               Check if containers are running
        logs                 View container logs
        web                  Open the web UI in your browser

      Face Operations:
        detect               Detect faces in an image
        recognize            Recognize faces against known subjects
        verify               Compare two faces for similarity
        add-subject          Add a known face/subject to a collection
        list-subjects        List all known subjects
        delete-subject       Remove a subject from a collection

    EXAMPLES
    ────────
      # Start the service
      compreface start

      # Check service health
      compreface status

      # Detect all faces in a photo
      compreface detect photo.jpg

      # Detect with landmarks and age/gender plugins
      compreface detect photo.jpg --landmarks --demographics

      # Recognize faces (requires subjects added first)
      compreface recognize suspect.jpg

      # Recognize with similarity threshold
      compreface recognize suspect.jpg --threshold 0.9

      # Verify if two photos are the same person
      compreface verify face1.jpg face2.jpg

      # Verify with confidence output
      compreface verify face1.jpg face2.jpg --verbose

      # Add a known subject
      compreface add-subject --name "Jane Doe" --image jane.jpg

      # Process all images in a directory
      compreface detect ./evidence_photos/ --batch --output results.json

      # Export results as JSON
      compreface recognize suspect.jpg -o json > report.json

      # View logs for troubleshooting
      compreface logs --follow

      # Stop when done
      compreface stop

    ENVIRONMENT VARIABLES
    ─────────────────────
      COMPREFACE_API_KEY     API key for authenticated operations
      COMPREFACE_URL         API base URL (default: http://localhost:8000)
      COMPREFACE_DIR         CompreFace installation directory

    OUTPUT FORMATS
    ──────────────
      --output text          Human-readable table (default)
      --output json          JSON for processing/piping
      --output csv           CSV spreadsheet format

    INVESTIGATION WORKFLOW
    ──────────────────────
      1. Start CompreFace:          compreface start
      2. Add known subjects:        compreface add-subject --name "POI" --image ref.jpg
      3. Run recognition on evidence:  compreface recognize evidence/*.jpg --batch
      4. Cross-reference with OSINT:   recon <username_from_match> --deep
      5. Extract photo metadata:       exiftool evidence/*.jpg
      6. Document findings:            compreface recognize evidence.jpg -o json >> case.json

    WORKS WELL WITH
    ────────────────
      • exiftool   — Extract GPS, camera, and timestamp metadata from photos
      • sherlock    — If you identify a person, search for their online presence
      • maigret     — Deep username search across 3,000+ sites
      • blackbird   — Search dating & social platforms for identified persons
      • toutatis    — Extract contact info from Instagram profiles
      • strings     — Find hidden text or URLs embedded in image files

    REQUIREMENTS
    ────────────
      • Docker Desktop for macOS (docker + docker-compose)
      • ~4GB RAM allocated to Docker (for the ML models)
      • ~2GB disk space for container images

    CUSTOM MODELS
    ─────────────
      CompreFace supports multiple face recognition models:
        • Mobilenet      — Fast, lower accuracy (good for real-time)
        • FaceNet        — Balanced speed and accuracy
        • ArcFace r100   — Highest accuracy (default)
        • Mobilenet GPU  — GPU-accelerated variant
        • ArcFace GPU    — GPU-accelerated highest accuracy

      To switch models, use the custom-builds/ directory:
        compreface stop
        cp custom-builds/FaceNet/docker-compose.yml .
        compreface start

    TROUBLESHOOTING
    ───────────────
      "Connection refused"    → Service not started. Run: compreface start
      "No API key"            → Set COMPREFACE_API_KEY or create one in web UI
      "Out of memory"         → Increase Docker memory to 4GB+ in Docker Desktop
      "Port 8000 in use"      → Change port: compreface start --port 8001
      Slow first request      → ML model loading. Wait ~30s after start.

    VERSION
    ───────
      CompreFace CLI v1.0.0 (wrapping CompreFace v1.2.0)
      Part of Project RECON v3.0.0

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ---------------------------------------------------------------------------
# Docker helpers
# ---------------------------------------------------------------------------

def _compose_cmd() -> list[str]:
    """Return the docker-compose base command."""
    # Try docker compose (v2) first, fall back to docker-compose (v1)
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, check=True,
        )
        return ["docker", "compose", "-f", str(COMPOSE_FILE)]
    except Exception:
        return ["docker-compose", "-f", str(COMPOSE_FILE)]


def _env_args() -> list[str]:
    """Return --env-file arg if .env exists."""
    if ENV_FILE.exists():
        return ["--env-file", str(ENV_FILE)]
    return []


def _docker_available() -> bool:
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def _api_url() -> str:
    return os.environ.get("COMPREFACE_URL", DEFAULT_API_URL)


def _api_key() -> str | None:
    return os.environ.get("COMPREFACE_API_KEY")


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_start(args: argparse.Namespace) -> int:
    """Start CompreFace Docker containers."""
    if not _docker_available():
        print("✗ Docker is not running. Start Docker Desktop first.")
        return 1

    print("Starting CompreFace containers...")
    cmd = _compose_cmd() + _env_args() + ["up", "-d"]
    result = subprocess.run(cmd, cwd=str(TOOL_DIR))

    if result.returncode == 0:
        print("✓ CompreFace started")
        print(f"  Web UI:  {_api_url()}")
        print("  Note:    First startup takes ~60s to pull images and ~30s to load ML models")
    return result.returncode


def cmd_stop(args: argparse.Namespace) -> int:
    """Stop CompreFace Docker containers."""
    print("Stopping CompreFace containers...")
    cmd = _compose_cmd() + _env_args() + ["down"]
    result = subprocess.run(cmd, cwd=str(TOOL_DIR))
    if result.returncode == 0:
        print("✓ CompreFace stopped")
    return result.returncode


def cmd_restart(args: argparse.Namespace) -> int:
    """Restart CompreFace Docker containers."""
    print("Restarting CompreFace containers...")
    cmd = _compose_cmd() + _env_args() + ["restart"]
    result = subprocess.run(cmd, cwd=str(TOOL_DIR))
    if result.returncode == 0:
        print("✓ CompreFace restarted")
    return result.returncode


def cmd_status(args: argparse.Namespace) -> int:
    """Check if CompreFace containers are running."""
    if not _docker_available():
        print("✗ Docker is not running")
        return 1

    cmd = _compose_cmd() + _env_args() + ["ps"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(TOOL_DIR))
    print(result.stdout)

    # Quick health check
    try:
        import urllib.request
        req = urllib.request.Request(f"{_api_url()}/healthcheck")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print("✓ CompreFace API is healthy")
                return 0
    except Exception:
        pass

    print("⚠ CompreFace API not responding (may still be loading)")
    return 1


def cmd_logs(args: argparse.Namespace) -> int:
    """View CompreFace container logs."""
    cmd = _compose_cmd() + _env_args() + ["logs"]
    if getattr(args, "follow", False):
        cmd.append("-f")
    cmd.extend(["--tail", str(getattr(args, "lines", 100))])
    return subprocess.run(cmd, cwd=str(TOOL_DIR)).returncode


def cmd_web(args: argparse.Namespace) -> int:
    """Open the CompreFace web UI."""
    url = _api_url()
    print(f"Opening {url} ...")
    subprocess.run(["open", url])
    return 0


def _api_request(endpoint: str, image_path: str | None = None,
                 method: str = "POST", data: dict | None = None) -> dict:
    """Make an API request to CompreFace."""
    import urllib.request
    import urllib.error

    api_key = _api_key()
    url = f"{_api_url()}/api/v1/{endpoint}"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    body = data or {}
    if image_path:
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        body["file"] = img_b64

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"✗ API error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError:
        print("✗ Cannot connect to CompreFace. Is the service running?", file=sys.stderr)
        print("  Run: compreface start", file=sys.stderr)
        sys.exit(1)


def _format_output(data: dict | list, fmt: str = "text") -> str:
    """Format API response for output."""
    if fmt == "json":
        return json.dumps(data, indent=2)
    elif fmt == "csv":
        if isinstance(data, list) and data:
            keys = data[0].keys()
            lines = [",".join(keys)]
            for row in data:
                lines.append(",".join(str(row.get(k, "")) for k in keys))
            return "\n".join(lines)
        return json.dumps(data)
    else:
        return json.dumps(data, indent=2)


def cmd_detect(args: argparse.Namespace) -> int:
    """Detect faces in an image."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first (create one at the web UI)")
        return 1

    images = []
    target = Path(args.image)
    if target.is_dir():
        images = sorted(target.glob("*.jpg")) + sorted(target.glob("*.png")) + sorted(target.glob("*.jpeg"))
    else:
        images = [target]

    all_results = []
    for img in images:
        print(f"  Detecting faces in {img.name}...")
        result = _api_request("detection/detect", str(img))
        faces = result.get("result", [])
        print(f"    → {len(faces)} face(s) found")
        all_results.append({"image": str(img), "faces": len(faces), "details": faces})

    output = _format_output(all_results, getattr(args, "output", "text"))
    print(output)
    return 0


def cmd_recognize(args: argparse.Namespace) -> int:
    """Recognize faces against known subjects."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first")
        return 1

    print(f"  Recognizing faces in {args.image}...")
    result = _api_request("recognition/recognize", args.image)
    faces = result.get("result", [])

    for face in faces:
        subjects = face.get("subjects", [])
        box = face.get("box", {})
        if subjects:
            best = subjects[0]
            conf = best.get("similarity", 0) * 100
            print(f"    ✓ Match: {best.get('subject', 'unknown')} ({conf:.1f}% confidence)")
            print(f"      Box: ({box.get('x_min')},{box.get('y_min')}) → ({box.get('x_max')},{box.get('y_max')})")
        else:
            print(f"    ? Unknown face at ({box.get('x_min')},{box.get('y_min')})")

    fmt = getattr(args, "output", "text")
    if fmt in ("json", "csv"):
        print(_format_output(result, fmt))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Compare two faces for similarity."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first")
        return 1

    print(f"  Comparing {args.image1} ↔ {args.image2}...")

    with open(args.image1, "rb") as f:
        img1_b64 = base64.b64encode(f.read()).decode()
    with open(args.image2, "rb") as f:
        img2_b64 = base64.b64encode(f.read()).decode()

    result = _api_request("verification/verify", data={
        "source_image": img1_b64,
        "target_image": img2_b64,
    })

    similarities = result.get("result", [])
    for r in similarities:
        sim = r.get("face_matches", [{}])
        for m in sim:
            score = m.get("similarity", 0) * 100
            if score > 90:
                print(f"    ✓ MATCH — {score:.1f}% similarity (same person)")
            elif score > 70:
                print(f"    ~ POSSIBLE — {score:.1f}% similarity (likely same person)")
            else:
                print(f"    ✗ NO MATCH — {score:.1f}% similarity (different people)")

    fmt = getattr(args, "output", "text")
    if fmt in ("json", "csv"):
        print(_format_output(result, fmt))
    return 0


def cmd_add_subject(args: argparse.Namespace) -> int:
    """Add a known face/subject."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first")
        return 1

    print(f"  Adding subject '{args.name}' from {args.image}...")
    result = _api_request(f"recognition/faces?subject={args.name}", args.image)
    img_id = result.get("image_id", "")
    print(f"    ✓ Subject '{args.name}' added (image_id: {img_id})")
    return 0


def cmd_list_subjects(args: argparse.Namespace) -> int:
    """List all known subjects."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first")
        return 1

    result = _api_request("recognition/subjects", method="GET")
    subjects = result.get("subjects", [])
    if not subjects:
        print("  No subjects found. Add some with: compreface add-subject")
    else:
        print(f"  {len(subjects)} subject(s):")
        for s in subjects:
            print(f"    • {s}")
    return 0


def cmd_delete_subject(args: argparse.Namespace) -> int:
    """Delete a subject."""
    if not _api_key():
        print("✗ Set COMPREFACE_API_KEY first")
        return 1

    result = _api_request(f"recognition/faces?subject={args.name}", method="DELETE")
    print(f"  ✓ Subject '{args.name}' deleted")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compreface",
        description="CompreFace — Face Recognition & Image Intelligence for RECON",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"compreface-cli {VERSION}")

    sub = parser.add_subparsers(dest="command", title="subcommands")

    # Service management
    sub.add_parser("start", help="Start CompreFace Docker containers")
    sub.add_parser("stop", help="Stop CompreFace Docker containers")
    sub.add_parser("restart", help="Restart all containers")
    sub.add_parser("status", help="Check if containers are running")
    sub.add_parser("web", help="Open the web UI in browser")

    p_logs = sub.add_parser("logs", help="View container logs")
    p_logs.add_argument("-f", "--follow", action="store_true", help="Follow log output")
    p_logs.add_argument("-n", "--lines", type=int, default=100, help="Number of lines (default: 100)")

    # Face operations
    p_detect = sub.add_parser("detect", help="Detect faces in an image")
    p_detect.add_argument("image", help="Image file or directory of images")
    p_detect.add_argument("--landmarks", action="store_true", help="Include facial landmarks")
    p_detect.add_argument("--demographics", action="store_true", help="Include age/gender estimation")
    p_detect.add_argument("-o", "--output", choices=["text", "json", "csv"], default="text")

    p_rec = sub.add_parser("recognize", help="Recognize faces against known subjects")
    p_rec.add_argument("image", help="Image file to recognize")
    p_rec.add_argument("--threshold", type=float, default=0.0, help="Minimum similarity threshold (0.0-1.0)")
    p_rec.add_argument("-o", "--output", choices=["text", "json", "csv"], default="text")

    p_ver = sub.add_parser("verify", help="Compare two faces for similarity")
    p_ver.add_argument("image1", help="First image")
    p_ver.add_argument("image2", help="Second image")
    p_ver.add_argument("-o", "--output", choices=["text", "json", "csv"], default="text")
    p_ver.add_argument("-v", "--verbose", action="store_true", help="Show detailed comparison data")

    p_add = sub.add_parser("add-subject", help="Add a known face/subject")
    p_add.add_argument("--name", required=True, help="Subject name")
    p_add.add_argument("--image", required=True, help="Reference image of the subject")

    sub.add_parser("list-subjects", help="List all known subjects")

    p_del = sub.add_parser("delete-subject", help="Remove a subject")
    p_del.add_argument("--name", required=True, help="Subject name to remove")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMAND_MAP = {
    "start": cmd_start,
    "stop": cmd_stop,
    "restart": cmd_restart,
    "status": cmd_status,
    "logs": cmd_logs,
    "web": cmd_web,
    "detect": cmd_detect,
    "recognize": cmd_recognize,
    "verify": cmd_verify,
    "add-subject": cmd_add_subject,
    "list-subjects": cmd_list_subjects,
    "delete-subject": cmd_delete_subject,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    handler = COMMAND_MAP.get(args.command)
    if handler:
        sys.exit(handler(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
