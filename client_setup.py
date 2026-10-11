"""Windows-only, standard-library customer sandbox configurator. No network calls."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import uuid

ROOT = Path(__file__).absolute().parent
PACKAGE = "safe-order-summary"
VERSIONS = ("1.0.0", "1.1.0")
SKILL = ".agents/skills/safe-order-summary"
PAYLOADS = {
    "SKILL.md": f"{SKILL}/SKILL.md",
    "summarize.py": f"{SKILL}/scripts/summarize.py",
    "orders.csv": f"{SKILL}/assets/orders.csv",
    "defaults.json": ".client-setup/public.json",
}
EFFECTIVE = ".client-setup/effective.json"
IDENTITY = ".client-setup/identity.json"
STATE = ".client-setup/state.json"
MANAGED = set(PAYLOADS.values()) | {EFFECTIVE}
TRANSACTION_FILES = MANAGED | {STATE, IDENTITY}
LIMIT = 128 * 1024


class SetupError(Exception):
    """Only fixed error codes cross the CLI boundary; never echo input or OS errors."""


def fail(code):
    raise SetupError(code)


def encode(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def hashed(value):
    return digest(encode(value))


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", value):
        fail("invalid_identifier")
    return value


def no_links(path):
    """Reject Windows junctions/reparse points, symlinks, and file hardlinks."""
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            fail("linked_path_rejected")
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            fail("hardlink_rejected")


def safe(root, relative):
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        fail("unsafe_path")
    parts = relative.split("/")
    if any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in parts):
        fail("unsafe_path")
    if PurePosixPath(relative).is_absolute():
        fail("unsafe_path")
    for part in parts:
        if re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part):
            fail("unsafe_path")
    root = root.absolute()
    path = root.joinpath(*parts)
    no_links(path)
    if not path.resolve().is_relative_to(root.resolve()):
        fail("unsafe_path")
    return path


def read(path):
    no_links(path)
    try:
        if not path.is_file() or path.stat().st_size > LIMIT:
            fail("invalid_file")
        return path.read_bytes()
    except FileNotFoundError:
        return None


def optional_read(path):
    no_links(path)
    return read(path) if path.exists() else None


def parse(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                fail("duplicate_json_key")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=pairs)
    except (ValueError, TypeError, UnicodeError):
        fail("invalid_json")


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        fail("invalid_schema")


def put(path, data):
    no_links(path)
    if optional_read(path) == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    no_links(path)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        no_links(path)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def remove(path):
    no_links(path)
    if path.exists():
        path.unlink()


def utc():
    return datetime.now(timezone.utc).isoformat()


def host_key():
    # A local binding, not hardware attestation. No account, registry, or secret reads.
    import socket
    return hashlib.sha256(socket.gethostname().casefold().encode()).hexdigest()[:16]


def file_version(path):
    """Read VERSIONINFO without launching an unknown runtime or reading its config."""
    try:
        api = ctypes.windll.version
        size = api.GetFileVersionInfoSizeW(str(path), None)
        if not size or size > LIMIT:
            return None
        buf = ctypes.create_string_buffer(size)
        if not api.GetFileVersionInfoW(str(path), 0, size, buf):
            return None
        pointer, length = ctypes.c_void_p(), ctypes.c_uint()
        if not api.VerQueryValueW(buf, "\\", ctypes.byref(pointer), ctypes.byref(length)) or length.value < 52:
            return None
        numbers = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32))
        if numbers[0] != 0xFEEF04BD:
            return None
        return ".".join(str(n) for n in (numbers[2] >> 16, numbers[2] & 65535, numbers[3] >> 16, numbers[3] & 65535))
    except (AttributeError, OSError, ValueError):
        return None


def probe():
    result = {"python": sys.version.split()[0], "host_fingerprint": host_key(), "platform": "windows"}
    result["runtimes"] = {}
    for name in ("codex", "openclaw", "hermes", "clash"):
        path = shutil.which(name)
        result["runtimes"][name] = {
            "found_on_path": bool(path),
            "file_version": file_version(path) if path and path.lower().endswith(".exe") else None,
            "status": "awaiting_configuration" if name != "clash" else "optional_probe_only",
        }
    return result


class Engine:
    def __init__(self, root=ROOT):
        if os.name != "nt":
            fail("windows_only")
        self.root = Path(root).absolute()
        no_links(self.root)
        if not self.root.is_dir():
            fail("project_missing")
        self.fail_at = None  # Test injection only; no CLI or environment switch.

    def path(self, relative):
        return safe(self.root, relative)

    def target(self, customer, instance):
        return self.path(f"sandboxes/{identifier(customer)}/{identifier(instance)}")

    def identity(self, customer, instance):
        return {"schema": 1, "customer": customer, "instance": instance,
                "host_fingerprint": host_key(), "target": str(self.target(customer, instance)).casefold(),
                "runtime": "local-python-sample"}

    def control(self, kind, customer, instance):
        return self.path(f".control/{kind}/{identifier(customer)}--{identifier(instance)}.json")

    @contextmanager
    def lock(self, customer, instance):
        import msvcrt
        path = self.control("locks", customer, instance)
        path.parent.mkdir(parents=True, exist_ok=True)
        no_links(path)
        with path.open("a+b") as stream:
            if path.stat().st_size == 0:
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                fail("instance_busy")
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    def guard_identity(self, customer, instance, allow_pending=False):
        target = self.target(customer, instance)
        raw = optional_read(safe(target, IDENTITY))
        if raw is not None:
            if parse(raw) != self.identity(customer, instance):
                fail("instance_identity_mismatch")
        elif target.exists() and any(target.iterdir()) and not allow_pending:
            fail("unowned_target_not_empty")
        return raw

    def package(self, version):
        if version not in VERSIONS:
            fail("unapproved_version")
        lock = parse(read(self.path("sources.lock.json")))
        fields(lock, ("schema", "source", "recipes"))
        if lock["schema"] != 1 or lock["source"] != "bundled://safe-order-summary" or set(lock["recipes"]) != set(VERSIONS):
            fail("untrusted_source")
        recipe_raw = read(self.path(f"recipes/{version}.json"))
        if not valid_hash(lock["recipes"][version]) or digest(recipe_raw) != lock["recipes"][version]:
            fail("recipe_hash_mismatch")
        recipe = parse(recipe_raw)
        fields(recipe, ("schema", "package", "version", "source", "files"))
        if recipe["schema"] != 1 or recipe["package"] != PACKAGE or recipe["version"] != version or recipe["source"] != f"bundled://{PACKAGE}@{version}":
            fail("untrusted_source")
        if not isinstance(recipe["files"], list) or len(recipe["files"]) != len(PAYLOADS):
            fail("invalid_file_manifest")
        contents, seen = {}, set()
        for item in recipe["files"]:
            fields(item, ("source", "target", "sha256"))
            safe(self.root, item["source"])
            safe(self.root, item["target"])
            if item["source"] not in PAYLOADS or item["target"] != PAYLOADS[item["source"]] or item["source"] in seen:
                fail("unmanaged_path")
            seen.add(item["source"])
            raw = read(self.path(f"packages/{version}/{item['source']}"))
            if not valid_hash(item["sha256"]) or digest(raw) != item["sha256"]:
                fail("payload_hash_mismatch")
            contents[item["target"]] = raw
        return contents, digest(recipe_raw)

    def settings(self, public):
        fields(public, ("currency", "minimum_total"))
        if public != {"currency": "USD", "minimum_total": 0}:
            fail("invalid_public_settings")
        return dict(public)

    def desired(self, customer, version):
        contents, recipe_hash = self.package(version)
        config = self.settings(parse(contents[".client-setup/public.json"]))
        overlay_raw = optional_read(self.path(f"customers/{identifier(customer)}/overrides.json"))
        overlay = parse(overlay_raw) if overlay_raw is not None else {}
        fields(overlay, (), ("currency", "minimum_total", "credential_refs"))
        if "currency" in overlay and overlay["currency"] not in ("CNY", "USD", "EUR"):
            fail("invalid_override")
        if "minimum_total" in overlay and (type(overlay["minimum_total"]) is not int or not 0 <= overlay["minimum_total"] <= 10000):
            fail("invalid_override")
        refs = overlay.get("credential_refs", [])
        if not isinstance(refs, list) or len(refs) > 8 or any(not isinstance(r, str) or not re.fullmatch(r"env:[A-Z][A-Z0-9_]{0,63}", r) for r in refs):
            fail("credential_reference_required")
        config.update({k: overlay[k] for k in ("currency", "minimum_total") if k in overlay})
        machine_raw = optional_read(self.path(f"machines/{host_key()}.json"))
        machine = parse(machine_raw) if machine_raw is not None else {}
        fields(machine, (), ("task_timeout_seconds", "optional_tools"))
        timeout = machine.get("task_timeout_seconds", 10)
        if type(timeout) is not int or not 1 <= timeout <= 60 or machine.get("optional_tools", []) not in ([], ["clash"]):
            fail("invalid_machine_settings")
        # Credential references stay in the owner file; their values are never read.
        contents[EFFECTIVE] = encode(config)
        inputs = {"recipe_sha256": recipe_hash, "overrides_sha256": digest(overlay_raw),
                  "machine_sha256": digest(machine_raw), "credential_reference_count": len(refs)}
        return contents, inputs, config, timeout

    def state(self, customer, instance):
        raw = optional_read(safe(self.target(customer, instance), STATE))
        if raw is None:
            return None, None
        value = parse(raw)
        fields(value, ("schema", "identity_sha256", "version", "recipe_sha256", "managed", "inputs"))
        if value["schema"] != 1 or value["identity_sha256"] != hashed(self.identity(customer, instance)) or value["version"] not in VERSIONS:
            fail("invalid_state")
        if set(value["managed"]) != MANAGED or not all(valid_hash(h) for h in value["managed"].values()) or not valid_hash(value["recipe_sha256"]):
            fail("invalid_state")
        fields(value["inputs"], ("recipe_sha256", "overrides_sha256", "machine_sha256", "credential_reference_count"))
        if value["inputs"]["recipe_sha256"] != value["recipe_sha256"] or any(value["inputs"][k] is not None and not valid_hash(value["inputs"][k]) for k in ("overrides_sha256", "machine_sha256")):
            fail("invalid_state")
        return value, raw

    def build_plan(self, action, customer, instance, version):
        identifier(customer)
        identifier(instance)
        self.guard_identity(customer, instance)
        if self.control("pending", customer, instance).exists():
            fail("recovery_required")
        contents, inputs, config, _ = self.desired(customer, version)
        current_state, state_raw = self.state(customer, instance)
        if action == "update" and current_state is None:
            fail("install_required")
        if action == "configure" and current_state and current_state["version"] != version:
            fail("use_update_for_version_change")
        entries = []
        for relative in sorted(MANAGED):
            raw = optional_read(safe(self.target(customer, instance), relative))
            before = digest(raw)
            expected = current_state["managed"][relative] if current_state else None
            if before != expected:
                fail("managed_file_drift")
            after = digest(contents[relative])
            entries.append({"path": relative, "before": before, "after": after,
                            "change": "keep" if before == after else "add" if before is None else "replace"})
        plan = {"schema": 1, "action": action, "identity": self.identity(customer, instance), "version": version,
                "inputs": inputs, "settings": config, "state_before": digest(state_raw), "files": entries,
                "previous_version": current_state["version"] if current_state else None}
        previous_config = parse(read(safe(self.target(customer, instance), EFFECTIVE))) if current_state else None
        if previous_config is not None:
            fields(previous_config, ("currency", "minimum_total"))
            if previous_config["currency"] not in ("CNY", "USD", "EUR") or type(previous_config["minimum_total"]) is not int or not 0 <= previous_config["minimum_total"] <= 10000:
                fail("invalid_state")
        plan["settings_before"] = previous_config
        plan["release_change"] = "add_largest_order_result" if version == "1.1.0" and plan["previous_version"] != version else "none"
        return plan, contents

    def preview(self, action, customer, instance, version):
        with self.lock(customer, instance):
            plan, _ = self.build_plan(action, customer, instance, version)
            token = hashed(plan)
            put(self.path(f".control/plans/{token}.json"), encode(plan))
            return {"status": "confirmation_required", "plan_id": token, "plan": plan, "environment": probe()}

    def object(self, raw):
        if raw is None:
            return None
        key = digest(raw)
        path = self.path(f".control/objects/{key}")
        previous = optional_read(path)
        if previous is not None and previous != raw:
            fail("snapshot_corrupt")
        put(path, raw)
        return key

    def object_read(self, key):
        if key is None:
            return None
        if not valid_hash(key):
            fail("invalid_snapshot")
        raw = read(self.path(f".control/objects/{key}"))
        if digest(raw) != key:
            fail("snapshot_corrupt")
        return raw

    def journal(self, customer, instance):
        raw = optional_read(self.control("pending", customer, instance))
        if raw is None:
            return None
        value = parse(raw)
        fields(value, ("schema", "plan_id", "plan", "started_at", "files"))
        if value["schema"] != 1 or hashed(value["plan"]) != value["plan_id"]:
            fail("invalid_journal")
        plan = value["plan"]
        fields(plan, ("schema", "action", "identity", "version", "inputs", "settings", "settings_before", "release_change", "state_before", "files", "previous_version"))
        if plan["identity"] != self.identity(customer, instance) or plan["version"] not in VERSIONS or plan["action"] not in ("configure", "update"):
            fail("instance_identity_mismatch")
        if not isinstance(value["files"], dict) or set(value["files"]) != TRANSACTION_FILES:
            fail("invalid_journal")
        entries = plan["files"]
        if not isinstance(entries, list) or len(entries) != len(MANAGED):
            fail("invalid_journal")
        indexed = {}
        for entry in entries:
            fields(entry, ("path", "before", "after", "change"))
            if entry["path"] not in MANAGED or entry["path"] in indexed:
                fail("invalid_journal")
            indexed[entry["path"]] = entry
        for relative, pair in value["files"].items():
            fields(pair, ("before", "after"))
            self.object_read(pair["before"])
            self.object_read(pair["after"])
            if relative in MANAGED and pair != {k: indexed[relative][k] for k in ("before", "after")}:
                fail("invalid_journal")
        if value["files"][STATE]["before"] != plan["state_before"] or self.object_read(value["files"][IDENTITY]["after"]) != encode(plan["identity"]):
            fail("invalid_journal")
        return value

    def validate_recovery(self, customer, instance, journal):
        self.guard_identity(customer, instance, allow_pending=True)
        target = self.target(customer, instance)
        for relative, pair in journal["files"].items():
            current = digest(optional_read(safe(target, relative)))
            if current not in (pair["before"], pair["after"]):
                fail("recovery_drift")

    def checkpoint(self, name):
        if self.fail_at == name:
            raise RuntimeError("injected_failure")

    def acceptance(self, customer, instance, version, contents, config, timeout):
        target = self.target(customer, instance)
        for relative, raw in contents.items():
            if optional_read(safe(target, relative)) != raw:
                fail("installation_verification_failed")
        skill = contents[f"{SKILL}/SKILL.md"].decode("utf-8")
        if "name: safe-order-summary\n" not in skill or "scripts/summarize.py" not in skill:
            fail("skill_contract_invalid")
        command = [sys.executable, "-I", "-S", "-B", str(safe(target, f"{SKILL}/scripts/summarize.py")),
                   str(safe(target, f"{SKILL}/assets/orders.csv"))]
        environment = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ}
        try:
            run = subprocess.run(command, input=encode(config), capture_output=True, cwd=target,
                                 env=environment, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired):
            fail("sample_task_failed")
        if run.returncode or len(run.stdout) > LIMIT or run.stderr:
            fail("sample_task_failed")
        result = parse(run.stdout)
        from decimal import Decimal
        selected = [Decimal(s) for s in ("12.50", "27.50", "20.00") if Decimal(s) >= config["minimum_total"]]
        expected = {"currency": config["currency"], "order_count": len(selected),
                    "total": format(sum(selected, Decimal(0)), ".2f"), "version": version}
        if version == "1.1.0":
            expected["largest_order"] = format(max(selected, default=Decimal(0)), ".2f")
        if result != expected:
            fail("sample_result_mismatch")
        return {"installation": "passed", "loading": {"local_harness": "passed", "agent_runtime": "not_verified"},
                "business": {"status": "passed", "scope": "bundled_synthetic_orders_only", "result": result}}

    def apply(self, action, customer, instance, version, approve, recover="resume"):
        if not valid_hash(approve):
            fail("confirmation_required")
        with self.lock(customer, instance):
            journal = self.journal(customer, instance)
            if journal is None:
                if recover == "rollback":
                    fail("no_pending_transaction")
                replay = self.replay(action, customer, instance, version, approve)
                if replay is not None:
                    return replay
                plan, contents = self.build_plan(action, customer, instance, version)
                if hashed(plan) != approve:
                    fail("plan_changed_reconfirm")
                current_state, state_raw = self.state(customer, instance)
                new_state = {"schema": 1, "identity_sha256": hashed(plan["identity"]), "version": version,
                             "recipe_sha256": plan["inputs"]["recipe_sha256"],
                             "inputs": plan["inputs"],
                             "managed": {p: digest(raw) for p, raw in contents.items()}}
                all_contents = dict(contents, **{STATE: encode(new_state), IDENTITY: encode(plan["identity"])})
                pairs = {}
                for relative, raw in all_contents.items():
                    before = optional_read(safe(self.target(customer, instance), relative))
                    expected = ({p["path"]: p["before"] for p in plan["files"]}.get(relative)
                                if relative in MANAGED else plan["state_before"] if relative == STATE
                                else digest(encode(plan["identity"])) if before is not None else None)
                    if digest(before) != expected:
                        fail("plan_changed_reconfirm")
                    pairs[relative] = {"before": self.object(before), "after": self.object(raw)}
                journal = {"schema": 1, "plan_id": approve, "plan": plan, "started_at": utc(), "files": pairs}
                put(self.control("pending", customer, instance), encode(journal))
            if journal["plan_id"] != approve or journal["plan"]["action"] != action or journal["plan"]["version"] != version:
                fail("pending_plan_mismatch")
            self.validate_recovery(customer, instance, journal)
            self.checkpoint("journal")
            if recover == "rollback":
                return self.rollback(customer, instance, journal)
            contents, inputs, config, timeout = self.desired(customer, version)
            if inputs != journal["plan"]["inputs"] or any(digest(contents[p]) != journal["files"][p]["after"] for p in MANAGED):
                fail("recovery_inputs_changed")
            target = self.target(customer, instance)
            for index, relative in enumerate([IDENTITY] + sorted(MANAGED)):
                put(safe(target, relative), self.object_read(journal["files"][relative]["after"]))
                self.checkpoint(f"file-{index}")
            acceptance = self.acceptance(customer, instance, version, contents, config, timeout)
            self.checkpoint("accepted")
            put(safe(target, STATE), self.object_read(journal["files"][STATE]["after"]))
            self.checkpoint("state")
            receipt = {"schema": 1, "status": "completed", "plan_id": approve,
                       "identity": journal["plan"]["identity"], "version": version,
                       "started_at": journal["started_at"], "inputs": inputs,
                       "files": journal["plan"]["files"], "acceptance": acceptance,
                       "runtime_status": "awaiting_configuration",
                       "continue": f"python client_setup.py check --customer {customer} --instance {instance}"}
            self.save_receipt(customer, instance, receipt)
            self.checkpoint("receipt")
            remove(self.control("pending", customer, instance))
            return receipt

    def replay(self, action, customer, instance, version, approve):
        path = self.path(f".control/receipts/{approve}-completed.json")
        raw = optional_read(path)
        if raw is None:
            return None
        self.guard_identity(customer, instance)
        receipt = parse(raw)
        fields(receipt, ("schema", "status", "plan_id", "identity", "version", "started_at", "inputs",
                         "files", "acceptance", "runtime_status", "continue"))
        plan = parse(read(self.path(f".control/plans/{approve}.json")))
        if hashed(plan) != approve or plan["identity"] != self.identity(customer, instance) or plan["action"] != action or plan["version"] != version:
            fail("plan_changed_reconfirm")
        state, _ = self.state(customer, instance)
        contents, inputs, config, timeout = self.desired(customer, version)
        if not state or state["version"] != version:
            return None  # A prior pending operation may have been rolled back after its receipt write.
        if state["recipe_sha256"] != inputs["recipe_sha256"] or inputs != plan["inputs"] or state["inputs"] != inputs:
            fail("plan_changed_reconfirm")
        if any(digest(contents[p]) != state["managed"][p] for p in MANAGED):
            fail("plan_changed_reconfirm")
        if not isinstance(receipt["started_at"], str) or not re.fullmatch(r"[0-9T:.+\-]{20,40}", receipt["started_at"]):
            fail("invalid_receipt")
        acceptance = self.acceptance(customer, instance, version, contents, config, timeout)
        expected = {"schema": 1, "status": "completed", "plan_id": approve,
                    "identity": self.identity(customer, instance), "version": version, "started_at": receipt["started_at"],
                    "inputs": inputs, "files": plan["files"], "acceptance": acceptance,
                    "runtime_status": "awaiting_configuration",
                    "continue": f"python client_setup.py check --customer {customer} --instance {instance}"}
        if receipt != expected:
            fail("invalid_receipt")
        return dict(expected, replayed=True)

    def save_receipt(self, customer, instance, receipt):
        suffix = "rollback" if receipt["status"] == "rolled_back" else "completed"
        put(self.path(f".control/receipts/{receipt['plan_id']}-{suffix}.json"), encode(receipt))
        put(self.control("latest", customer, instance), encode(receipt))

    def rollback(self, customer, instance, journal):
        target = self.target(customer, instance)
        for relative in sorted(MANAGED) + [STATE, IDENTITY]:
            data = self.object_read(journal["files"][relative]["before"])
            path = safe(target, relative)
            remove(path) if data is None else put(path, data)
        # Only empty directories created for explicitly managed paths are candidates.
        parents = {p for name in TRANSACTION_FILES for p in safe(target, name).parents if p.is_relative_to(target)}
        for directory in sorted(parents, key=lambda p: len(p.parts), reverse=True):
            no_links(directory)
            try:
                directory.rmdir()
            except OSError:
                pass
        receipt = {"schema": 1, "status": "rolled_back", "plan_id": journal["plan_id"],
                   "identity": journal["plan"]["identity"], "started_at": journal["started_at"],
                   "restored_version": journal["plan"]["previous_version"], "runtime_status": "awaiting_configuration"}
        self.save_receipt(customer, instance, receipt)
        remove(self.control("pending", customer, instance))
        return receipt

    def check(self, customer, instance):
        identifier(customer)
        identifier(instance)
        pending = self.journal(customer, instance)
        self.guard_identity(customer, instance, allow_pending=pending is not None)
        if pending:
            self.validate_recovery(customer, instance, pending)
            return {"status": "recovery_required", "plan_id": pending["plan_id"],
                    "action": pending["plan"]["action"], "version": pending["plan"]["version"],
                    "environment": probe(), "acceptance": {"installation": "incomplete", "loading": "not_verified", "business": "not_run"}}
        state, _ = self.state(customer, instance)
        if state is None:
            return {"status": "not_installed", "environment": probe()}
        for relative, expected in state["managed"].items():
            if digest(optional_read(safe(self.target(customer, instance), relative))) != expected:
                fail("managed_file_drift")
        contents, inputs, config, timeout = self.desired(customer, state["version"])
        if inputs["recipe_sha256"] != state["recipe_sha256"]:
            fail("recipe_hash_mismatch")
        if inputs != state["inputs"] or any(digest(raw) != state["managed"][p] for p, raw in contents.items()):
            return {"status": "configuration_update_available", "version": state["version"], "environment": probe(),
                    "acceptance": {"installation": "passed", "loading": "not_verified", "business": "not_run"}}
        return {"status": "healthy", "version": state["version"], "environment": probe(),
                "acceptance": self.acceptance(customer, instance, state["version"], contents, config, timeout),
                "latest_receipt": f".control/latest/{customer}--{instance}.json"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local customer sandbox: configure / check / update")
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("configure", "check", "update"):
        sub = subparsers.add_parser(action)
        sub.add_argument("--customer", required=True)
        sub.add_argument("--instance", default="local")
        sub.add_argument("--brief", help="Project-relative computer brief; read-only guidance, never installation")
        if action != "check":
            sub.add_argument("--version", choices=VERSIONS, default="1.0.0" if action == "configure" else "1.1.0")
            sub.add_argument("--approve", help="The exact SHA-256 plan_id reviewed by the user")
            sub.add_argument("--recover", choices=("resume", "rollback"), default="resume")
    args = parser.parse_args(argv)
    try:
        if args.brief:
            if getattr(args, "approve", None) or getattr(args, "recover", "resume") != "resume":
                fail("guidance_is_read_only")
            from tools import computer_guide
            try:
                result = computer_guide.from_file(args.brief, args.action, args.customer, args.instance)
            except computer_guide.cs.SetupError as error:
                fail(str(error))
            print(encode(result).decode(), end="")
            return 0
        engine = Engine()
        if args.action == "check":
            result = engine.check(args.customer, args.instance)
        elif args.approve:
            result = engine.apply(args.action, args.customer, args.instance, args.version, args.approve, args.recover)
        elif args.recover == "rollback":
            fail("confirmation_required")
        else:
            result = engine.preview(args.action, args.customer, args.instance, args.version)
        print(encode(result).decode(), end="")
        if result["status"] in ("not_installed", "recovery_required", "configuration_update_available"):
            return 2
        return 0
    except SetupError as error:
        print(json.dumps({"status": "blocked", "error": str(error)}))
        return 2
    except Exception:
        print(json.dumps({"status": "failed", "error": "local_operation_failed", "next": "Run check; use the pending plan to resume or roll back."}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
