import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import client_setup as cs


def copy_fixture(destination):
    """Explicit public files only. Never copy an existing sandbox or customer data."""
    for relative in ["sources.lock.json"] + [f"recipes/{v}.json" for v in cs.VERSIONS] + [f"packages/{v}/{p}" for v in cs.VERSIONS for p in cs.PAYLOADS]:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((cs.ROOT / relative).read_bytes())


class SetupTests(unittest.TestCase):
    def setUp(self):
        base = cs.ROOT / ".test-runs"
        base.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name)
        copy_fixture(self.root)
        self.engine = cs.Engine(self.root)
        self.customer, self.instance = "alpha", "local"

    def tearDown(self):
        self.tmp.cleanup()

    def preview(self, action="configure", version="1.0.0"):
        return self.engine.preview(action, self.customer, self.instance, version)

    def apply(self, preview=None, action="configure", version="1.0.0", recover="resume"):
        plan = preview or self.preview(action, version)
        return self.engine.apply(action, self.customer, self.instance, version, plan["plan_id"], recover)

    def overlay(self, value):
        path = self.root / "customers/alpha/overrides.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(cs.encode(value))
        return path

    def target(self, relative):
        return self.engine.target(self.customer, self.instance) / relative

    def assertBlocked(self, code, function, *args, **kwargs):
        with self.assertRaises(cs.SetupError) as context:
            function(*args, **kwargs)
        self.assertEqual(str(context.exception), code)

    def repin_recipe(self, value, version="1.0.0"):
        raw = cs.encode(value)
        (self.root / f"recipes/{version}.json").write_bytes(raw)
        lock_path = self.root / "sources.lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["recipes"][version] = cs.digest(raw)
        lock_path.write_bytes(cs.encode(lock))

    def test_preview_is_reviewable_and_does_not_install(self):
        preview = self.preview()
        self.assertEqual(preview["status"], "confirmation_required")
        self.assertEqual({p["change"] for p in preview["plan"]["files"]}, {"add"})
        self.assertFalse(self.engine.target("alpha", "local").exists())
        self.assertTrue((self.root / f".control/plans/{preview['plan_id']}.json").is_file())

    def test_install_runs_task_and_does_not_claim_agent_loading(self):
        receipt = self.apply()
        self.assertEqual(receipt["acceptance"]["business"]["result"],
                         {"currency": "USD", "order_count": 3, "total": "60.00", "version": "1.0.0"})
        self.assertEqual(receipt["acceptance"]["loading"]["agent_runtime"], "not_verified")
        self.assertEqual(self.engine.check("alpha", "local")["status"], "healthy")

    def test_same_approved_command_replays_without_file_rewrites(self):
        preview = self.preview()
        first = self.apply(preview)
        paths = [p for p in self.root.rglob("*") if p.is_file() and "/locks/" not in p.as_posix()]
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        second = self.apply(preview)
        self.assertTrue(second.pop("replayed"))
        self.assertEqual(first, second)
        self.assertEqual(before, {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})
        self.assertEqual({p["change"] for p in self.preview()["plan"]["files"]}, {"keep"})

    def test_customer_override_is_preserved_through_update(self):
        owner = self.overlay({"currency": "CNY", "minimum_total": 20, "credential_refs": ["env:EXAMPLE_ONLY"]})
        before = owner.read_bytes(), owner.stat().st_mtime_ns
        self.apply()
        preview = self.preview("update", "1.1.0")
        changes = {x["path"]: x["change"] for x in preview["plan"]["files"]}
        self.assertEqual(changes[f"{cs.SKILL}/SKILL.md"], "replace")
        self.assertEqual(changes[cs.EFFECTIVE], "keep")
        receipt = self.apply(preview, "update", "1.1.0")
        self.assertEqual(receipt["acceptance"]["business"]["result"],
                         {"currency": "CNY", "order_count": 2, "total": "47.50", "largest_order": "27.50", "version": "1.1.0"})
        self.assertEqual(before, (owner.read_bytes(), owner.stat().st_mtime_ns))

    def test_changed_overlay_invalidates_approval(self):
        preview = self.preview()
        self.overlay({"currency": "EUR"})
        self.assertBlocked("plan_changed_reconfirm", self.apply, preview)
        self.assertFalse(self.engine.target("alpha", "local").exists())

    def test_new_customer_settings_need_update_and_check_is_read_only(self):
        self.apply()
        self.overlay({"minimum_total": 20})
        before = {str(p): p.stat().st_mtime_ns for p in self.root.rglob("*") if p.is_file()}
        result = self.engine.check("alpha", "local")
        self.assertEqual(result["status"], "configuration_update_available")
        self.assertEqual(before, {str(p): p.stat().st_mtime_ns for p in self.root.rglob("*") if p.is_file()})
        self.apply(self.preview("update", "1.0.0"), "update", "1.0.0")
        self.assertEqual(self.engine.check("alpha", "local")["acceptance"]["business"]["result"]["total"], "47.50")

    def test_bad_payload_hash_is_rejected_before_target_writes(self):
        (self.root / "packages/1.0.0/summarize.py").write_text("raise Exception('untrusted')")
        self.assertBlocked("payload_hash_mismatch", self.preview)
        self.assertFalse(self.engine.target("alpha", "local").exists())

    def test_bad_recipe_hash_is_rejected(self):
        with (self.root / "recipes/1.0.0.json").open("ab") as stream:
            stream.write(b" ")
        self.assertBlocked("recipe_hash_mismatch", self.preview)

    def test_unknown_version_is_not_guessed(self):
        self.assertBlocked("unapproved_version", self.engine.preview, "configure", "alpha", "local", "9.9.9")

    def test_traversal_absolute_ads_and_reserved_paths_are_rejected(self):
        recipe = json.loads((self.root / "recipes/1.0.0.json").read_bytes())
        for unsafe in ("../outside", "Z:/SYNTHETIC-ONLY", "/outside", "a\\b", "a:secret", "a/../b", "NUL", "a.", "a//b"):
            with self.subTest(path=unsafe):
                value = json.loads(json.dumps(recipe))
                value["files"][0]["target"] = unsafe
                self.repin_recipe(value)
                self.assertBlocked("unsafe_path", self.preview)

    def test_safe_looking_unmanaged_path_is_rejected(self):
        recipe = json.loads((self.root / "recipes/1.0.0.json").read_bytes())
        recipe["files"][0]["target"] = "unrelated.txt"
        self.repin_recipe(recipe)
        self.assertBlocked("unmanaged_path", self.preview)

    def test_invalid_customer_cannot_escape(self):
        for customer in ("../alpha", "Alpha", "a/b", "a:b", "", "a" * 33):
            self.assertBlocked("invalid_identifier", self.engine.preview, "configure", customer, "local", "1.0.0")

    def test_unowned_nonempty_target_is_left_untouched(self):
        path = self.target("owner.txt")
        path.parent.mkdir(parents=True)
        path.write_text("unrelated")
        self.assertBlocked("unowned_target_not_empty", self.preview)
        self.assertEqual(path.read_text(), "unrelated")

    def test_copied_instance_cannot_overwrite_another_customer(self):
        self.apply()
        foreign = self.engine.target("bravo", "local")
        foreign.parent.mkdir(parents=True)
        shutil.copytree(self.engine.target("alpha", "local"), foreign)
        self.assertBlocked("instance_identity_mismatch", self.engine.preview, "configure", "bravo", "local", "1.0.0")

    def test_machine_identity_change_is_rejected(self):
        self.apply()
        with patch.object(cs, "host_key", return_value="different-host"):
            self.assertBlocked("instance_identity_mismatch", self.engine.check, "alpha", "local")

    def test_drift_is_not_overwritten_or_snapshotted(self):
        self.apply()
        marker = b"SYNTHETIC_SECRET_DO_NOT_COPY_771"
        self.target(cs.EFFECTIVE).write_bytes(marker)
        self.assertBlocked("managed_file_drift", self.preview)
        self.assertFalse(any(marker in p.read_bytes() for p in (self.root / ".control").rglob("*") if p.is_file()))

    def test_update_requires_prior_install(self):
        self.assertBlocked("install_required", self.preview, "update", "1.1.0")

    def test_configure_requires_update_for_new_version(self):
        self.apply()
        self.assertBlocked("use_update_for_version_change", self.preview, "configure", "1.1.0")

    def test_recovery_after_each_commit_boundary(self):
        for boundary in ("journal", "file-0", "file-1", "file-5", "accepted", "state", "receipt"):
            with self.subTest(boundary=boundary):
                self.instance = "case-" + boundary
                preview = self.preview()
                self.engine.fail_at = boundary
                with self.assertRaises(RuntimeError):
                    self.apply(preview)
                self.engine = cs.Engine(self.root)
                self.assertEqual(self.engine.check("alpha", self.instance)["status"], "recovery_required")
                self.assertEqual(self.apply(preview)["status"], "completed")
                self.assertFalse(self.engine.control("pending", "alpha", self.instance).exists())

    def test_actual_process_exit_releases_lock_and_resumes(self):
        preview = self.preview()
        code = ("import os,sys; from pathlib import Path; import client_setup as c; "
                "e=c.Engine(Path(sys.argv[1])); "
                "e.checkpoint=lambda name: os._exit(91) if name=='file-2' else None; "
                "e.apply('configure','alpha','local','1.0.0',sys.argv[2])")
        run = subprocess.run([sys.executable, "-B", "-c", code, str(self.root), preview["plan_id"]], cwd=cs.ROOT, capture_output=True)
        self.assertEqual(run.returncode, 91)
        self.assertEqual(cs.Engine(self.root).check("alpha", "local")["status"], "recovery_required")
        self.assertEqual(self.apply(preview)["status"], "completed")

    def test_pending_rejects_different_plan_and_changed_inputs(self):
        preview = self.preview()
        self.engine.fail_at = "file-1"
        with self.assertRaises(RuntimeError):
            self.apply(preview)
        self.engine.fail_at = None
        self.assertBlocked("pending_plan_mismatch", self.engine.apply, "configure", "alpha", "local", "1.0.0", "f" * 64)
        self.overlay({"currency": "EUR"})
        self.assertBlocked("recovery_inputs_changed", self.apply, preview)
        self.assertEqual(self.apply(preview, recover="rollback")["status"], "rolled_back")

    def test_partial_update_rolls_back_exact_bytes_preserving_unknown_file(self):
        self.apply()
        before = {p: self.target(p).read_bytes() for p in cs.TRANSACTION_FILES}
        unknown = self.target("customer-note.txt")
        unknown.write_text("synthetic-owner-note")
        preview = self.preview("update", "1.1.0")
        self.engine.fail_at = "file-2"
        with self.assertRaises(RuntimeError):
            self.apply(preview, "update", "1.1.0")
        self.engine.fail_at = None
        receipt = self.apply(preview, "update", "1.1.0", "rollback")
        self.assertEqual(receipt["status"], "rolled_back")
        self.assertEqual(before, {p: self.target(p).read_bytes() for p in cs.TRANSACTION_FILES})
        self.assertEqual(unknown.read_text(), "synthetic-owner-note")

    def test_recovery_refuses_new_drift_and_corrupt_snapshot(self):
        preview = self.preview()
        self.engine.fail_at = "file-2"
        with self.assertRaises(RuntimeError):
            self.apply(preview)
        self.engine.fail_at = None
        path = self.target(f"{cs.SKILL}/SKILL.md")
        path.write_text("new external edit")
        self.assertBlocked("recovery_drift", self.apply, preview)
        journal = self.engine.journal("alpha", "local")
        path.write_bytes(self.engine.object_read(journal["files"][f"{cs.SKILL}/SKILL.md"]["after"]))
        object_key = journal["files"][cs.EFFECTIVE]["after"]
        (self.root / f".control/objects/{object_key}").write_bytes(b"corrupt")
        self.assertBlocked("snapshot_corrupt", self.apply, preview)

    def test_unknown_fields_and_literal_secrets_are_not_accepted_or_echoed(self):
        fake = "SYNTHETIC_NOT_A_REAL_KEY"
        self.overlay({"api_key": fake})
        self.assertBlocked("invalid_schema", self.preview)
        self.overlay({"credential_refs": ["SYNTHETIC_NOT_A_REAL_KEY"]})
        self.assertBlocked("credential_reference_required", self.preview)
        self.overlay({"currency": "SYNTHETIC_NOT_A_REAL_KEY"})
        self.assertBlocked("invalid_override", self.preview)

    def test_unlisted_sensitive_files_and_environment_values_are_excluded(self):
        marker = b"SYNTHETIC_SECRET_SENTINEL_887732"
        sensitive = self.root / "customers/alpha/.env"
        sensitive.parent.mkdir(parents=True)
        sensitive.write_bytes(marker)
        (self.root / "packages/1.0.0/cookies.txt").write_bytes(marker)
        self.overlay({"credential_refs": ["env:CLIENT_SETUP_TEST_SECRET"]})
        visited = []
        original_read = cs.read
        def audited(path):
            visited.append(path)
            return original_read(path)
        with patch.dict(os.environ, {"CLIENT_SETUP_TEST_SECRET": marker.decode()}), patch.object(cs, "read", side_effect=audited):
            receipt = self.apply()
        self.assertNotIn(sensitive, visited)
        self.assertNotIn(self.root / "packages/1.0.0/cookies.txt", visited)
        self.assertNotIn(marker, cs.encode(receipt))
        for directory in (self.root / ".control", self.root / "sandboxes"):
            self.assertFalse(any(marker in p.read_bytes() for p in directory.rglob("*") if p.is_file()))

    def test_task_subprocess_has_no_credential_environment(self):
        original_run = subprocess.run
        environments = []
        def audited(*args, **kwargs):
            environments.append(kwargs["env"])
            return original_run(*args, **kwargs)
        with patch.dict(os.environ, {"CLIENT_SETUP_SECRET": "SYNTHETIC"}), patch.object(cs.subprocess, "run", side_effect=audited):
            self.apply()
        self.assertTrue(environments)
        self.assertTrue(all(set(env) <= {"SYSTEMROOT", "WINDIR"} for env in environments))

    def test_hardlink_and_directory_junction_are_rejected(self):
        outside = self.root / "outside.txt"
        outside.write_text("synthetic")
        source = self.root / "packages/1.0.0/orders.csv"
        source.unlink()
        os.link(outside, source)
        self.assertBlocked("hardlink_rejected", self.preview)
        source.unlink()
        source.write_bytes((cs.ROOT / "packages/1.0.0/orders.csv").read_bytes())
        outside_dir = self.root / "outside-dir"
        outside_dir.mkdir()
        junction = self.root / "sandboxes"
        run = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside_dir)], capture_output=True)
        self.assertEqual(run.returncode, 0, "Unable to create isolated test junction")
        try:
            self.assertBlocked("linked_path_rejected", self.preview)
            self.assertEqual(list(outside_dir.iterdir()), [])
        finally:
            os.rmdir(junction)

    def test_second_process_is_blocked_by_instance_lock(self):
        with self.engine.lock("alpha", "local"):
            code = ("import sys; from pathlib import Path; import client_setup as c; "
                    "e=c.Engine(Path(sys.argv[1])); "
                    "e.preview('configure','alpha','local','1.0.0')")
            run = subprocess.run([sys.executable, "-B", "-c", code, str(self.root)], cwd=cs.ROOT, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(b"instance_busy", run.stderr)

    def test_no_external_runtime_or_proxy_commands_are_executed(self):
        with patch.object(cs.shutil, "which", return_value="example.cmd"), patch.object(cs.subprocess, "run", side_effect=AssertionError("must not launch")):
            info = cs.probe()
        for name in ("codex", "openclaw", "hermes"):
            self.assertEqual(info["runtimes"][name]["status"], "awaiting_configuration")
            self.assertIsNone(info["runtimes"][name]["file_version"])
        self.assertEqual(info["runtimes"]["clash"]["status"], "optional_probe_only")

    def test_business_failure_stays_recoverable(self):
        preview = self.preview()
        with patch.object(self.engine, "acceptance", side_effect=cs.SetupError("sample_task_failed")):
            self.assertBlocked("sample_task_failed", self.apply, preview)
        self.assertEqual(self.engine.check("alpha", "local")["status"], "recovery_required")
        self.assertEqual(self.apply(preview)["status"], "completed")

    def test_rollback_after_receipt_boundary_allows_fresh_install(self):
        preview = self.preview()
        self.engine.fail_at = "receipt"
        with self.assertRaises(RuntimeError):
            self.apply(preview)
        self.engine.fail_at = None
        self.assertEqual(self.apply(preview, recover="rollback")["status"], "rolled_back")
        fresh = self.preview()
        self.assertEqual(self.apply(fresh)["status"], "completed")

    def test_machine_or_reference_change_requires_a_new_plan(self):
        self.apply()
        machine = self.root / "machines" / f"{cs.host_key()}.json"
        machine.parent.mkdir()
        machine.write_bytes(cs.encode({"task_timeout_seconds": 15, "optional_tools": ["clash"]}))
        self.assertEqual(self.engine.check("alpha", "local")["status"], "configuration_update_available")
        self.apply()
        self.overlay({"credential_refs": ["env:SYNTHETIC_REFERENCE"]})
        self.assertEqual(self.engine.check("alpha", "local")["status"], "configuration_update_available")


if __name__ == "__main__":
    unittest.main()
