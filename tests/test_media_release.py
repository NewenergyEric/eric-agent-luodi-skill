import json
import unittest
from test_release import ReleaseTests
from tools import release
import client_setup as cs


class MediaReleaseTests(ReleaseTests):
    # Reuse only the sandbox fixture, not the parent test methods.
    def test_binary_tamper_is_rejected(self):
        p = self.root / "assets/readme/hero-zh.gif"
        p.write_bytes(p.read_bytes() + b"changed")
        with self.assertRaisesRegex(release.ReleaseError, "media_pin_mismatch"):
            release.check(self.root)

    def test_forged_binary_type_is_rejected_even_with_matching_hash(self):
        name = "assets/readme/hero-zh.gif"
        data = b"synthetic invalid binary"
        (self.root / name).write_bytes(data)
        p = self.root / "showcase-files.json"
        pins = json.loads(p.read_bytes())
        pins["files"][name] = {"bytes": len(data), "sha256": cs.digest(data)}
        p.write_bytes(cs.encode(pins))
        with self.assertRaisesRegex(release.ReleaseError, "public_binary_type_mismatch"):
            release.check(self.root)

    def test_unapproved_image_path_is_rejected_before_open(self):
        self.manifest["files"].append("assets/private-capture.png")
        self.write_manifest()
        with self.assertRaisesRegex(release.ReleaseError, "unapproved_binary_path"):
            release.check(self.root)

    def test_missing_media_pin_is_rejected(self):
        p = self.root / "showcase-files.json"
        pins = json.loads(p.read_bytes())
        pins["files"].pop("assets/readme/hero-zh.gif")
        p.write_bytes(cs.encode(pins))
        with self.assertRaisesRegex(release.ReleaseError, "invalid_media_pin_manifest"):
            release.check(self.root)

    def test_private_render_output_is_rejected(self):
        self.manifest["files"].append("motion/out/raw.mp4")
        self.write_manifest()
        with self.assertRaisesRegex(release.ReleaseError, "private_path_excluded"):
            release.check(self.root)


# Share setup/cleanup helpers without duplicating the existing test suite.
for _name in list(dir(ReleaseTests)):
    if _name.startswith("test_") and _name not in MediaReleaseTests.__dict__:
        setattr(MediaReleaseTests, _name, None)
del ReleaseTests
