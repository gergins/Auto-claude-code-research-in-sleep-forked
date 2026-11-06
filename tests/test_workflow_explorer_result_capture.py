"""Local result capture + deterministic indexing contract tests (no model calls)."""
import importlib.util
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "prototypes" / "workflow-explorer" / "overnight_demo.py"
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("aris_research_local_demo", SCRIPT)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class LocalResearchConnectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "records"
        override = patch.object(demo, "RECORD_DIR", self.folder)
        override.start()
        self.addCleanup(override.stop)

    def test_import_and_preserve_unverified_result(self):
        payload = {
            "skill": "auto-review-loop",
            "invocation": '/auto-review-loop "proven open source for video relay service"',
            "execution_status": "evidence-attached",
            "review_status": "accepted",
            "result": "LiveKit + LiveKit SIP. Sources: https://github.com/livekit/livekit and https://github.com/livekit/sip",
        }
        info = demo.store_record(payload)
        self.assertTrue(info["saved_locally"])
        self.assertEqual(info["skill"], "auto-review-loop")
        record = demo.load_record()
        self.assertEqual(record["result"], payload["result"])
        self.assertEqual(record["review_status"], "not-independently-verified")
        self.assertEqual(record["execution_status"], "unverified")
        self.assertEqual(info["sha256"], demo.metadata(record)["sha256"])

    def test_detect_candidates_and_no_false_verification(self):
        demo.store_record({"skill": "auto-review-loop",
                           "result": "LiveKit, Janus, Jitsi and RFC 9248. https://github.com/livekit/sip"})
        summary = demo.assess_record()
        self.assertIn("LiveKit", summary["mentions"])
        self.assertIn("Janus", summary["mentions"])
        self.assertIn("RFC 9248", summary["mentions"])
        self.assertEqual(summary["candidate_urls"], ["https://github.com/livekit/sip"])
        self.assertFalse(summary["claims_independently_verified"])
        self.assertFalse(summary["source_links_checked"])

    def test_reject_empty_or_invalid_record(self):
        for bad in ({}, {"result": ""}, {"result": "x", "skill": "../escape"},
                    {"result": "x" * 100001}, ["not a record"]):
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(ValueError):
                    demo.store_record(bad)

if __name__ == "__main__":
    unittest.main()
