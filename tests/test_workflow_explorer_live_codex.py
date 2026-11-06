"""Live ARIS/Codex adapter contract tests; no AI calls."""
from __future__ import annotations

import importlib.util
import inspect
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "prototypes" / "workflow-explorer" / "live_codex.py"
spec = importlib.util.spec_from_file_location("aris_live_codex", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class LiveResearchSafetyTests(unittest.TestCase):
    def setUp(self):
        self.runner = mod.LiveCodex()

    def test_block_unknown_skill_without_process(self):
        with self.assertRaisesRegex(ValueError, "not allowlisted"):
            self.runner.start("any-shell-command", "Examine a VRS open-source architecture.", 10)

    def test_block_invalid_runtime(self):
        with patch.object(mod.shutil, "which", return_value="codex"):
            with self.assertRaisesRegex(ValueError, "Choose 10, 60 or 480"):
                self.runner.start("research-lit", "Examine a VRS open-source architecture.", 10_000)

    def test_block_missing_codex_executable(self):
        with patch.object(mod.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                self.runner.start("research-lit", "Examine a VRS open-source architecture.", 10)

    def test_selected_skill_must_be_on_disk(self):
        with patch.object(mod, "SKILLS", Path(__file__).parent / "missing-codex-skills"):
            with self.assertRaisesRegex(ValueError, "missing"):
                self.runner.start("research-lit", "Examine a VRS open-source architecture.", 10)

    def test_only_approved_durations_and_statuses(self):
        self.assertEqual(mod.DURATIONS[10], 600)
        self.assertEqual(mod.DURATIONS[480], 28800)
        self.assertEqual(self.runner.snapshot()["review_status"], "not-independently-verified")
        self.assertEqual(self.runner.snapshot()["acceptance"], "not-accepted")

    def test_subprocess_policy_is_restricted(self):
        source = inspect.getsource(mod.LiveCodex._worker)
        self.assertIn('"--sandbox"', source)
        self.assertIn('"read-only"', source)
        self.assertNotIn("shell=True", source)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", source)
        self.assertNotIn("--yolo", source)
        self.assertIn("shutil.copytree(SKILLS", source)


if __name__ == "__main__":
    unittest.main()
