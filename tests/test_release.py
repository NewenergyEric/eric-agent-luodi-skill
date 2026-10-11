import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid
import zipfile

import client_setup as cs
from tools import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        base = cs.ROOT / ".test-runs"
        base.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.tmp.name)
        self.manifest = json.loads((cs.ROOT / "release-files.json").read_bytes())
        for name in self.manifest["files"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((cs.ROOT / name).read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self):
        (self.root / "release-files.json").write_bytes(cs.encode(self.manifest))

    def test_clean_source_passes_without_claiming_publication_ready(self):
        report, payloads = release.check(self.root)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(set(payloads), set(self.manifest["files"]))
        self.assertFalse(report["publication_ready"])
        self.assertIn("license_not_selected", report["publication_blockers"])
        self.assertEqual("upstream_license_review_pending" in report["publication_blockers"], self.manifest["upstream_review"] != "completed")

    def test_private_files_are_never_read_or_archived(self):
        marker = "SYNTHETIC_PRIVATE_SENTINEL_" + uuid.uuid4().hex
        names = ["customers/sample/.env", "machines/example.json", ".control/latest/sample.json",
                 "DELIVERY.md", "DEMO-LATEST.json", "validation/results.json", ".private/old.txt",
                 ".local-tests/independent-install/README.md",
                 ".local-tests/independent-install/.control/latest/sample.json"]
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(marker, encoding="utf-8")
        seen, original = [], cs.read
        def audit(path):
            seen.append(path)
            return original(path)
        with patch.object(cs, "read", side_effect=audit):
            result = release.build(self.root)
        self.assertEqual(result["status"], "passed")
        self.assertFalse(any(self.root / name in seen for name in names))
        with zipfile.ZipFile(self.root / result["artifact"]) as archive:
            self.assertEqual(set(archive.namelist()), set(self.manifest["files"]))
            self.assertFalse(any(marker.encode() in archive.read(name) for name in archive.namelist()))
        self.assertTrue(all((self.root / name).read_text(encoding="utf-8") == marker for name in names))

    def test_repeated_build_is_deterministic(self):
        one = release.build(self.root)
        path = self.root / one["artifact"]
        before = path.stat().st_mtime_ns
        two = release.build(self.root)
        self.assertEqual(one["artifact_sha256"], two["artifact_sha256"])
        self.assertEqual(before, path.stat().st_mtime_ns)
        self.assertFalse(two["uploaded"])

    def test_private_manifest_addition_is_rejected_before_read(self):
        name = "customers/private/.env"
        self.manifest["files"].append(name)
        self.write_manifest()
        seen, original = [], cs.read
        def audit(path):
            seen.append(path)
            return original(path)
        with patch.object(cs, "read", side_effect=audit), self.assertRaisesRegex(release.ReleaseError, "private_path_excluded"):
            release.check(self.root)
        self.assertNotIn(self.root / name, seen)

    def test_nested_local_test_snapshot_is_rejected_before_read(self):
        names = [".local-tests/independent-install/README.md",
                 "docs/.local-tests/receipt.json", "docs/.LOCAL-TESTS/receipt.json"]
        for name in names:
            with self.subTest(path=name):
                self.manifest["files"].append(name)
                self.write_manifest()
                seen, original = [], cs.read
                def audit(path):
                    seen.append(path)
                    return original(path)
                with patch.object(cs, "read", side_effect=audit), self.assertRaisesRegex(release.ReleaseError, "private_path_excluded"):
                    release.check(self.root)
                self.assertNotIn(self.root / name, seen)
                self.manifest["files"].pop()

    def test_path_escape_and_case_duplicate_are_rejected(self):
        self.manifest["files"].append("../outside.txt")
        self.write_manifest()
        with self.assertRaises(release.ReleaseError):
            release.check(self.root)
        self.manifest["files"].pop()
        self.manifest["files"].append("readme.md")
        self.write_manifest()
        with self.assertRaisesRegex(release.ReleaseError, "duplicate_release_path"):
            release.check(self.root)

    def test_findings_do_not_echo_matched_values(self):
        fake_token = "ghp_" + "A" * 36
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n" + fake_token + "\n")
        report, _ = release.check(self.root)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any(f["rule"] == "provider_token" for f in report["findings"]))
        self.assertNotIn(fake_token, json.dumps(report))
        self.assertNotIn("artifact", release.build(self.root))
        self.assertFalse((self.root / ".release").exists())

    def test_known_secret_and_identity_patterns(self):
        samples = {
            "private_key": "-----BEGIN " + "PRIVATE KEY-----",
            "auth_url": "https://" + "user:sample-value@" + "example.invalid",
            "proxy_link": "vmess" + "://" + "A" * 30,
            "private_ipv4": ".".join(("192", "168", "5", "6")),
            "email": "sample" + "@" + "example.invalid",
            "windows_absolute_path": "C" + ":/" + "Users/Synthetic/example",
            "literal_credential": 'api_key' + '=\"' + 'FAKE_VALUE_ONLY' + '\"',
        }
        for expected, sample in samples.items():
            with self.subTest(rule=expected):
                self.assertIn(expected, {x["rule"] for x in release.scan_text("README.md", sample)})
        self.assertEqual(release.scan_text("README.md", "SAMPLE_MACHINE", ["SAMPLE_MACHINE"])[0]["rule"], "local_identity")

    def test_extra_archive_member_is_rejected(self):
        _, payloads = release.check(self.root)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            for name, data in payloads.items():
                archive.writestr(name, data)
            archive.writestr("customers/sample/.env", b"synthetic")
        with self.assertRaisesRegex(release.ReleaseError, "archive_members_mismatch"):
            release.verify_zip(buf.getvalue(), payloads)

    def test_changed_archive_bytes_are_rejected(self):
        _, payloads = release.check(self.root)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            for name, data in payloads.items():
                archive.writestr(name, b"changed" if name == "README.md" else data)
        with self.assertRaisesRegex(release.ReleaseError, "archive_bytes_mismatch"):
            release.verify_zip(buf.getvalue(), payloads)

    def test_hardlinked_source_is_rejected(self):
        other = self.root / "other.txt"
        other.write_text("synthetic")
        target = self.root / "README.md"
        target.unlink()
        os.link(other, target)
        with self.assertRaisesRegex(release.ReleaseError, "unsafe_or_linked_release_path"):
            release.check(self.root)

    def test_changed_public_package_cannot_be_silently_repinned(self):
        with (self.root / "packages/1.0.0/summarize.py").open("ab") as stream:
            stream.write(b"\n# synthetic change\n")
        with self.assertRaisesRegex(release.ReleaseError, "payload_pin_mismatch"):
            release.check(self.root)

    def test_tracked_private_file_blocks_check(self):
        with patch.object(release, "git_state", return_value={"status":"repository", "history":"manual_review_required", "tracked_outside_allowlist":1}):
            result, _ = release.check(self.root)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("git_history_review_required", result["publication_blockers"])

    def test_crlf_is_reported(self):
        path = self.root / "README.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        report, _ = release.check(self.root)
        self.assertTrue(any(x["rule"] == "noncanonical_crlf" for x in report["findings"]))

    def test_license_cannot_be_marked_selected_without_file(self):
        self.manifest["license_status"] = "selected"
        self.write_manifest()
        with self.assertRaisesRegex(release.ReleaseError, "license_file_missing"):
            release.check(self.root)


if __name__ == "__main__":
    unittest.main()
