import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.evidence_pipeline.evaluation import verification
from app.evidence_pipeline.evaluation.comparison import _metrics


class VerificationEvaluationTests(unittest.TestCase):
    def test_saved_benchmark_evaluation_passes_and_writes_json(self):
        report = verification.run_verification_evaluation()
        self.assertEqual(report["summary"]["case_count"], 15)
        self.assertEqual(report["summary"]["failed_cases"], 0)
        self.assertTrue(Path(report["report_path"]).exists())
        saved = json.loads(Path(report["report_path"]).read_text(encoding="utf-8"))
        self.assertEqual(saved["summary"], report["summary"])
        self.assertEqual(saved["report_path"], report["report_path"])

    def test_evaluation_endpoint_returns_report(self):
        response = TestClient(app).post("/evaluations/verification")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["failed_cases"], 0)

    def test_metrics_expose_hard_case_false_merge(self):
        cases = [
            {"case_id": "clear", "verdict": "resolved", "ground_truth": {"expected_verdict": "resolved"}},
            {"case_id": "collision", "verdict": "resolved", "ground_truth": {"expected_verdict": "uncertain"}},
        ]
        metrics = _metrics(cases)
        self.assertEqual(metrics["false_merge_count"], 1)
        self.assertEqual(metrics["false_merge_rate"], 1.0)

        safe_agent = [
            {"case_id": "clear", "verdict": "resolved", "ground_truth": {"expected_verdict": "resolved"}},
            {"case_id": "collision", "verdict": "uncertain", "ground_truth": {"expected_verdict": "uncertain"}},
        ]
        self.assertEqual(_metrics(safe_agent)["false_merge_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
