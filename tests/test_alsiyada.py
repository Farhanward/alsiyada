from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from alsiyada.batch import evaluate
from alsiyada.datasets import convert_nvd
from alsiyada.policy import evaluate_manifest


class AlSiyadaTests(unittest.TestCase):
    def test_blocks_sensitive_cloud(self):
        result = evaluate_manifest({"data_classification": "restricted", "cloud_models_allowed": True, "audit_log": True, "region": "SA-RIYADH", "tool_allowlist": True})
        self.assertEqual(result["decision"], "BLOCK")

    def test_passes_local_audited_workload(self):
        result = evaluate_manifest({"data_classification": "internal", "cloud_models_allowed": False, "audit_log": True, "region": "SA-RIYADH", "tool_allowlist": True})
        self.assertEqual(result["decision"], "PASS")

    def test_convert_and_batch_fixture(self):
        with tempfile.TemporaryDirectory(dir="C:/Projects") as tmp:
            src = Path(tmp) / "nvd.jsonl"
            out = Path(tmp) / "manifests.jsonl"
            src.write_text('{"id":"CVE-1","severity":"HIGH"}\n{"id":"CVE-2","severity":"LOW"}\n', encoding="utf-8")
            convert_nvd(src, out)
            summary = evaluate(out)
            self.assertEqual(summary["errors"], 0)


if __name__ == "__main__":
    unittest.main()

