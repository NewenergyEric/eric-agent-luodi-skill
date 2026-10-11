"""Offline allowlisted source review and deterministic ZIP builder; no publishing."""
from __future__ import annotations

import argparse
import getpass
import io
import json
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import zipfile

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT))
import client_setup as cs

PRIVATE = {"customers", "machines", "sandboxes", ".control", ".demo-runs", ".test-runs", ".local-tests",
           "validation", ".private", ".release", ".git", "__pycache__", "node_modules", "out"}
PRIVATE_FILES = {"delivery.md", "open_source_prep.md", "demo-latest.json"}
SAFE_TOP = {"docs", "examples", "packages", "recipes", "tests", "tools", ".agents", "motion", "assets", ".github"}
SAFE_ROOT = {"README.md", "AGENTS.md", "THIRD_PARTY_NOTICES.md", "client_setup.py", "demo.py",
             "sources.lock.json", "release-files.json", ".gitignore", ".gitattributes", "LICENSE",
             "README.en.md", "product-evidence.json", "showcase-files.json"}
SKILL_FILES = {".agents/skills/client-setup/SKILL.md", ".agents/skills/client-setup/agents/openai.yaml"}
MAX_TOTAL = 64 * 1024 * 1024
MAX_BINARY = 8 * 1024 * 1024
BINARY_SLOTS = {f"assets/readme/hero-{lang}.{ext}" for lang in ("zh", "en") for ext in ("mp4", "gif", "webp", "png")}
BINARY_SLOTS |= {f"assets/readme/case-board-{lang}.png" for lang in ("zh", "en")}
BINARY_SLOTS.add("motion/public/fonts/setup-sans.woff2")
RULES = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    "provider_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,})\b"),
    "literal_credential": re.compile(r'''(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\b["']?\s*[:=]\s*["']([^\s"']{8,})["']'''),
    "auth_url": re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.I),
    "subscription_query": re.compile(r"https?://[^\s]+[?&](?:token|key|secret|password)=[^\s&]+", re.I),
    "proxy_link": re.compile(r"\b(?:ss|ssr|vmess|vless|trojan)://[A-Za-z0-9+/=_-]{8,}", re.I),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "private_ipv4": re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
    "windows_absolute_path": re.compile(r'''(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s"'<>),;]+'''),
    "personal_posix_path": re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+|" + r"/tmp/" + r"codex[^\s\"']*"),
}


class ReleaseError(Exception):
    pass


def stop(code):
    raise ReleaseError(code)


def local_identifiers(root):
    # Only non-secret identity metadata. Never enumerate environment variables.
    return [str(root), str(Path.home()), getpass.getuser(), socket.gethostname(), cs.host_key()]


def scan_text(name, content, identifiers=()):
    findings = []
    for rule, pattern in RULES.items():
        for match in pattern.finditer(content):
            synthetic = ":/".join(("Z", "SYNTHETIC-ONLY"))
            if rule == "windows_absolute_path" and name == "tests/test_client_setup.py" and match.group() == synthetic:
                continue
            findings.append({"file": name, "line": content.count("\n", 0, match.start()) + 1, "rule": rule})
    normalized = content.casefold().replace("\\\\", "\\")
    for value in identifiers:
        if not value or len(value) < 4:
            continue
        for match in re.finditer(re.escape(value.casefold()), normalized):
            findings.append({"file": name, "line": normalized.count("\n", 0, match.start()) + 1, "rule": "local_identity"})
    return findings


def allowed_path(root, name):
    if not isinstance(name, str) or len(name) > 180 or "*" in name or "?" in name:
        stop("invalid_release_path")
    parts = name.split("/")
    lowered = [p.casefold() for p in parts]
    if any(p in PRIVATE for p in lowered) or lowered[-1] in PRIVATE_FILES:
        stop("private_path_excluded")
    leaf = lowered[-1]
    if leaf.startswith((".env", "delivery", "open_source_prep", "id_rsa", "id_ed25519")) or any(word in leaf for word in ("cookie", "credential", "subscription")) or leaf.endswith((".key", ".pem", ".p12", ".pfx", ".log", ".zip", ".pyc")):
        stop("private_path_excluded")
    if len(parts) == 1:
        if name not in SAFE_ROOT:
            stop("unapproved_root_file")
    elif parts[0] not in SAFE_TOP or (parts[0] == ".agents" and name not in SKILL_FILES):
        stop("unapproved_source_directory")
    try:
        return cs.safe(root, name)
    except (cs.SetupError, ValueError, OSError):
        stop("unsafe_or_linked_release_path")


def read_public_binary(path, name, entry):
    # Generated public media only, with explicit paths, type, byte size and hash.
    # Binary review/decoding is separate; a text scanner cannot inspect pixels.
    cs.no_links(path)
    if not path.is_file() or path.stat().st_size > MAX_BINARY:
        stop("invalid_public_binary_size")
    data = path.read_bytes()
    if not isinstance(entry, dict) or set(entry) != {"bytes", "sha256"}:
        stop("invalid_media_pin")
    if len(data) != entry["bytes"] or cs.digest(data) != entry["sha256"]:
        stop("media_pin_mismatch")
    ext = path.suffix
    valid = ((ext == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n")) or
             (ext == ".gif" and data[:6] in (b"GIF87a", b"GIF89a")) or
             (ext == ".webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP") or
             (ext == ".woff2" and data[:4] == b"wOF2") or
             (ext == ".mp4" and data[4:8] == b"ftyp"))
    if not valid:
        stop("public_binary_type_mismatch")
    return data


def load_sources(root, identifiers=None):
    root = Path(root).absolute()
    cs.no_links(root)
    raw = cs.read(cs.safe(root, "release-files.json"))
    manifest = cs.parse(raw)
    cs.fields(manifest, ("schema", "files", "license_status", "upstream_review"))
    if manifest["schema"] != 1 or not isinstance(manifest["files"], list) or not manifest["files"]:
        stop("invalid_release_manifest")
    names = manifest["files"]
    if any(not isinstance(n, str) for n in names) or len({n.casefold() for n in names}) != len(names):
        stop("duplicate_release_path")
    required = {"README.md", "AGENTS.md", "client_setup.py", "demo.py", "sources.lock.json", "release-files.json",
                ".gitignore", ".gitattributes", "tools/release.py", "THIRD_PARTY_NOTICES.md"} | SKILL_FILES
    required |= {f"recipes/{v}.json" for v in cs.VERSIONS}
    required |= {f"packages/{v}/{p}" for v in cs.VERSIONS for p in cs.PAYLOADS}
    if not required <= set(names) or manifest["license_status"] not in ("not_selected", "selected") or manifest["upstream_review"] not in ("pending", "completed"):
        stop("incomplete_release_manifest")
    if manifest["license_status"] == "selected" and "LICENSE" not in names:
        stop("license_file_missing")
    # Validate every path before opening any member; private additions are never read.
    paths = {name: allowed_path(root, name) for name in names}
    identity_values = local_identifiers(root) if identifiers is None else identifiers
    binary_names = set(names) & BINARY_SLOTS
    if any(Path(n).suffix.lower() in (".png", ".gif", ".mp4", ".webp", ".woff2") and n not in BINARY_SLOTS for n in names):
        stop("unapproved_binary_path")
    media_pins = {}
    if binary_names:
        if "showcase-files.json" not in paths:
            stop("media_pin_manifest_missing")
        pin_manifest = cs.parse(cs.read(paths["showcase-files.json"]))
        if set(pin_manifest) != {"schema", "files"} or pin_manifest["schema"] != 1 or set(pin_manifest["files"]) != binary_names:
            stop("invalid_media_pin_manifest")
        media_pins = pin_manifest["files"]
    payloads, findings, total = {}, [], 0
    for name, path in paths.items():
        name_findings = scan_text("<filename>", name, identity_values)
        if name_findings:
            stop("sensitive_release_filename")
        if name in binary_names:
            data = read_public_binary(path, name, media_pins[name])
        elif name == "motion/package-lock.json":
            cs.no_links(path)
            if not path.is_file() or path.stat().st_size > 512 * 1024:
                stop("invalid_dependency_lock_size")
            data = path.read_bytes()
        else:
            data = cs.read(path)
        if data is None:
            stop("source_missing")
        total += len(data)
        if total > MAX_TOTAL:
            stop("release_too_large")
        if name in binary_names:
            payloads[name] = data
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeError:
            stop("non_utf8_source")
        if "\r\n" in content:
            findings.append({"file": name, "line": 1, "rule": "noncanonical_crlf"})
        findings.extend(scan_text(name, content, identity_values))
        payloads[name] = data
    # Validate the existing recipe pins without rewriting them.
    lock = cs.parse(payloads["sources.lock.json"])
    if lock.get("source") != "bundled://safe-order-summary":
        stop("source_pin_invalid")
    for version in cs.VERSIONS:
        raw_recipe = payloads[f"recipes/{version}.json"]
        if cs.digest(raw_recipe) != lock["recipes"][version]:
            stop("recipe_pin_mismatch")
        recipe = cs.parse(raw_recipe)
        if recipe.get("source") != f"bundled://{cs.PACKAGE}@{version}" or recipe.get("version") != version:
            stop("source_pin_invalid")
        if len(recipe["files"]) != len(cs.PAYLOADS):
            stop("invalid_package_manifest")
        seen = set()
        for item in recipe["files"]:
            if item["source"] not in cs.PAYLOADS or item["target"] != cs.PAYLOADS[item["source"]] or item["source"] in seen:
                stop("invalid_package_manifest")
            seen.add(item["source"])
            if cs.digest(payloads[f"packages/{version}/{item['source']}"]) != item["sha256"]:
                stop("payload_pin_mismatch")
    return manifest, payloads, findings


def git_state(root, names):
    executable = shutil.which("git")
    if not executable:
        return {"status": "unavailable", "history": "unverified"}
    def run(*args):
        return subprocess.run([executable, "-C", str(root), *args], capture_output=True, timeout=10)
    top = run("rev-parse", "--show-toplevel")
    if top.returncode:
        return {"status": "no_repository", "history": "none"}
    if Path(top.stdout.decode().strip()).resolve() != Path(root).resolve():
        return {"status": "ancestor_repository", "history": "manual_review_required"}
    tracked = run("ls-files", "-z")
    if tracked.returncode:
        stop("git_inspection_failed")
    tracked_names = {n for n in tracked.stdout.decode("utf-8").split("\0") if n}
    head = run("rev-parse", "--verify", "HEAD")
    return {"status": "repository", "tracked_count": len(tracked_names),
            "tracked_outside_allowlist": len(tracked_names - set(names)),
            "history": "manual_review_required" if head.returncode == 0 else "none"}


def check(root=ROOT, identifiers=None):
    manifest, payloads, findings = load_sources(root, identifiers)
    git = git_state(root, payloads)
    if git.get("tracked_outside_allowlist", 0):
        findings.append({"rule": "git_tracked_outside_allowlist"})
    blockers = []
    if manifest["license_status"] != "selected":
        blockers.append("license_not_selected")
    if manifest["upstream_review"] != "completed":
        blockers.append("upstream_license_review_pending")
    if git["history"] not in ("none",):
        blockers.append("git_history_review_required")
    report = {"status": "passed" if not findings else "blocked", "file_count": len(payloads),
              "files": {name: cs.digest(data) for name, data in sorted(payloads.items())},
              "findings": findings, "git": git,
              "publication_ready": not findings and not blockers, "publication_blockers": blockers,
              "scope": "allowlisted_current_source_only", "scan_is_not_a_guarantee": True}
    return report, payloads


def verify_zip(data, payloads):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            names = [item.filename for item in entries]
            if len(names) != len(set(names)) or set(names) != set(payloads):
                stop("archive_members_mismatch")
            if archive.comment or any(item.comment or item.extra or item.flag_bits & 1 or stat.S_ISLNK(item.external_attr >> 16) for item in entries):
                stop("archive_metadata_rejected")
            if sum(item.file_size for item in entries) > MAX_TOTAL:
                stop("archive_too_large")
            for item in entries:
                if item.file_size != len(payloads[item.filename]) or archive.read(item) != payloads[item.filename]:
                    stop("archive_bytes_mismatch")
    except (zipfile.BadZipFile, RuntimeError, OSError):
        stop("invalid_archive")


def build(root=ROOT):
    report, payloads = check(root)
    if report["status"] != "passed":
        return report
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payloads.items()):
            member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.create_system = 3
            member.external_attr = (stat.S_IFREG | 0o644) << 16
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, data)
    data = stream.getvalue()
    verify_zip(data, payloads)
    relative = f".release/client-setup-{cs.digest(data)[:16]}.zip"
    archive_path = cs.safe(Path(root), relative)
    if archive_path.exists():
        if archive_path.stat().st_size > MAX_TOTAL or archive_path.read_bytes() != data:
            stop("existing_archive_bytes_mismatch")
    else:
        cs.put(archive_path, data)
    # Verify the bytes stored on disk. No extraction and no private-tree traversal.
    path = cs.safe(Path(root), relative)
    cs.no_links(path)
    if path.stat().st_size > MAX_TOTAL:
        stop("archive_too_large")
    verify_zip(path.read_bytes(), payloads)
    return dict(report, artifact=relative, artifact_sha256=cs.digest(data), artifact_bytes=len(data), uploaded=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline source review; never uploads or chooses a license")
    parser.add_argument("action", choices=("check", "build"))
    parser.add_argument("--archive", help="Verify an existing project-relative review ZIP against current allowlisted source")
    args = parser.parse_args(argv)
    try:
        if args.action == "build" and args.archive:
            stop("invalid_arguments")
        if args.action == "build":
            report = build()
        else:
            report, payloads = check()
            if args.archive and report["status"] == "passed":
                path = cs.safe(ROOT, args.archive)
                if not args.archive.startswith(".release/") or path.stat().st_size > MAX_TOTAL:
                    stop("invalid_archive_path")
                verify_zip(path.read_bytes(), payloads)
                report["archive_verified"] = True
        print(cs.encode(report).decode(), end="")
        return 0 if report["status"] == "passed" else 2
    except (ReleaseError, cs.SetupError) as error:
        print(json.dumps({"status": "blocked", "error": str(error), "publication_ready": False}))
        return 2
    except Exception:
        print(json.dumps({"status": "blocked", "error": "release_check_failed", "publication_ready": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
