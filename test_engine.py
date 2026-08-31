"""Unit/integration tests reproducing the 4 examples from the README,
plus an edge case. Uses Python's built-in unittest, so no extra
dependencies are needed.

Run with:  python -m unittest discover -v
"""

import os
import sys
import unittest

# Allow running this file directly (adds project root to the import path).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from returns.models import EngineData, ReturnRequest
from returns.parser import (
    parse_category_rules,
    parse_scoring_rules,
    parse_decision_bands,
    parse_account_profiles,
    parse_account_links,
)
from returns.engine import Engine

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class ReturnRoutingEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = EngineData(
            category_rules=parse_category_rules(f"{DATA_DIR}/category_rules.json"),
            scoring_rules=parse_scoring_rules(f"{DATA_DIR}/scoring_rules.json"),
            decision_bands=parse_decision_bands(f"{DATA_DIR}/decision_bands.json"),
            account_profiles=parse_account_profiles(f"{DATA_DIR}/account_profiles.jsonl"),
            account_links=parse_account_links(f"{DATA_DIR}/account_links.jsonl"),
        )
        cls.engine = Engine(data)

    def test_example1_auto_approved_low_risk(self):
        req = ReturnRequest("r101", "u104", "ELECTRONICS", 10, 150, 365)
        d = self.engine.evaluate(req)
        self.assertEqual(d.decision, "AUTO_APPROVE")
        self.assertEqual(d.risk_score, 3)

    def test_example2_manual_review_linked_accounts(self):
        req = ReturnRequest("r103", "u101", "ELECTRONICS", 15, 250, 400)
        d = self.engine.evaluate(req)
        self.assertEqual(d.decision, "MANUAL_REVIEW")
        self.assertEqual(d.risk_score, 60)
        self.assertEqual(d.reason, "MEDIUM_RISK_SCORE")

    def test_example3_high_risk_rejection_linked_group(self):
        req = ReturnRequest("r104", "u107", "FURNITURE", 12, 800, 60)
        d = self.engine.evaluate(req)
        self.assertEqual(d.decision, "REJECT")
        self.assertEqual(d.risk_score, 95)
        self.assertEqual(d.reason, "HIGH_RISK_SCORE")

    def test_example4_return_window_expired(self):
        req = ReturnRequest("r105", "u104", "ELECTRONICS", 35, 150, 365)
        d = self.engine.evaluate(req)
        self.assertEqual(d.decision, "REJECT")
        self.assertIsNone(d.risk_score)
        self.assertEqual(d.reason, "RETURN_WINDOW_EXPIRED")

    def test_edge_case_unknown_category_falls_back_to_default_window(self):
        # DEFAULT window is 30 days, so 20 days since purchase should NOT
        # trigger a window-expired rejection.
        req = ReturnRequest("r999", "u104", "TOYS", 20, 100, 365)
        d = self.engine.evaluate(req)
        self.assertNotEqual(d.reason, "RETURN_WINDOW_EXPIRED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
