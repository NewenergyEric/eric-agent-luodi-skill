"""A relocated planning Skill must retain its license and all local references."""
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

import client_setup as cs
from tools import release


class StandaloneSkillTests(unittest.TestCase):
    def test_planning_skill_is_complete_without_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            skill = root / 'skills/eric-agent-luodi-skill'
            prefix = Path('.agents/skills/eric-agent-luodi-skill')
            for name in release.SKILL_FILES:
                destination = skill / Path(name).relative_to(prefix)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((cs.ROOT / name).read_bytes())
            self.assertEqual((skill / 'LICENSE').read_bytes(), (cs.ROOT / 'LICENSE').read_bytes())
            self.assertFalse((root / 'client_setup.py').exists())
            count = 0
            for path in skill.rglob('*.md'):
                for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                    parsed = urlsplit(link)
                    if parsed.scheme or not parsed.path:
                        continue
                    target = (path.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(target.is_relative_to(skill), link)
                    self.assertTrue(target.is_file(), link)
                    count += 1
            self.assertGreater(count, 0)


if __name__ == '__main__':
    unittest.main()
