"""Regression: run-state subprocess must emit UTF-8 under Windows cp1252."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "prototypes" / "workflow-explorer" / "overnight_demo.py"
sys.path.insert(0, str(MODULE.parent))
spec = importlib.util.spec_from_file_location("aris_offline_demo", MODULE)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class WindowsRunStateEncodingTests(unittest.TestCase):
    def test_state_command_forces_unicode_output(self):
        # The real run-state printer emits check marks and symbols not in cp1252.
        with patch.object(demo.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "run ✓", "")) as run:
            self.assertEqual(demo.state_cmd("status", "test", "id"), "run ✓")
            args, kwargs = run.call_args
            self.assertEqual(kwargs["encoding"], "utf-8")
            self.assertEqual(kwargs["env"]["PYTHONIOENCODING"], "utf-8")
            self.assertEqual(kwargs["env"]["PYTHONUTF8"], "1")
            self.assertEqual(kwargs["check"], False)
    def test_unicode_subprocess_failure_surfaces(self):
        with patch.object(demo.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failure")):
            with self.assertRaisesRegex(RuntimeError, "failure"):
                demo.state_cmd("start", "x", "y")
if __name__ == "__main__":
    unittest.main()
