import sys
import os
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "app.py"))

EXAMPLES = [
    "What is Mission Shakti and who can benefit from it?",
    "What support does Mission Vatsalya provide for children?",
    "What are the key components of Comprehensive Primary Health Care?",
    "Who is eligible under Mission Saksham?",
]


class TestExampleQueries(unittest.TestCase):
    def _run(self):
        at = AppTest.from_file(APP_PATH)
        at.run(timeout=60)
        return at

    def test_all_examples_displayed(self):
        at = self._run()
        buttons = [b for b in at.button if b.label in EXAMPLES]
        self.assertEqual(len(buttons), 4)
        for q in EXAMPLES:
            self.assertTrue(any(b.label == q for b in at.button))

    @patch("reasoning.analyze")
    def test_click_example_submits_correct_question(self, mock_analyze):
        mock_analyze.return_value = {"answer": "ok", "sources": [], "confidence": "High"}
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertTrue(mock_analyze.called)
        self.assertEqual(mock_analyze.call_args.args[0], EXAMPLES[0])
        self.assertTrue(any(getattr(t, "value", "") == EXAMPLES[0] for t in at.text_input))

    @patch("reasoning.analyze")
    def test_each_example_sends_own_question(self, mock_analyze):
        mock_analyze.return_value = {"answer": "ok", "sources": [], "confidence": "High"}
        for q in EXAMPLES:
            at = self._run()
            btn = [b for b in at.button if b.label == q][0]
            btn.click().run()
            self.assertEqual(mock_analyze.call_args.args[0], q)

    @patch("reasoning.analyze")
    def test_successful_response_displayed(self, mock_analyze):
        mock_analyze.return_value = {"answer": "ANSWER_OK", "sources": [], "confidence": "High"}
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertTrue(any("ANSWER_OK" in getattr(m, "value", "") for m in at.markdown))
        # loading indicator (spinner) should be gone after completion
        self.assertEqual(len(at.spinner), 0) if hasattr(at, "spinner") else True

    @patch("reasoning.analyze")
    def test_api_failure_shows_error(self, mock_analyze):
        mock_analyze.side_effect = RuntimeError("boom")
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertTrue(any("boom" in getattr(e, "value", "") for e in at.error) or any("boom" in getattr(m, "value", "") for m in at.markdown))
        self.assertFalse(at.exception)

    @patch("reasoning.analyze")
    def test_duplicate_submissions(self, mock_analyze):
        def slow(q, top_k=6):
            time.sleep(0.5)
            return {"answer": "ok", "sources": [], "confidence": "High"}

        mock_analyze.side_effect = slow
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        # a second click is a separate run; ensure no crash
        at2 = AppTest.from_file(APP_PATH)
        at2.run(timeout=60)
        btn2 = [b for b in at2.button if b.label == EXAMPLES[0]][0]
        btn2.click().run()
        self.assertFalse(at2.exception)

    @patch("reasoning.analyze")
    def test_switching_examples(self, mock_analyze):
        mock_analyze.return_value = {"answer": "FIRST_ANSWER", "sources": [], "confidence": "High"}
        at = self._run()
        btn0 = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn0.click().run()
        self.assertTrue(any("FIRST_ANSWER" in getattr(m, "value", "") for m in at.markdown))

        mock_analyze.return_value = {"answer": "SECOND_ANSWER", "sources": [], "confidence": "High"}
        btn1 = [b for b in at.button if b.label == EXAMPLES[1]][0]
        btn1.click().run()
        self.assertEqual(mock_analyze.call_args.args[0], EXAMPLES[1])
        self.assertTrue(any("SECOND_ANSWER" in getattr(m, "value", "") for m in at.markdown))

    @patch("reasoning.analyze")
    def test_empty_or_malformed_response(self, mock_analyze):
        mock_analyze.return_value = {"answer": "", "sources": [], "confidence": "Low"}
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertFalse(at.exception)

        mock_analyze.return_value = {}  # missing answer field
        at2 = self._run()
        btn2 = [b for b in at2.button if b.label == EXAMPLES[0]][0]
        btn2.click().run()
        self.assertFalse(at2.exception)

    @patch("reasoning.analyze")
    def test_manual_submission(self, mock_analyze):
        mock_analyze.return_value = {"answer": "MANUAL_OK", "sources": [], "confidence": "High"}
        at = self._run()
        at.text_input[0].set_value("custom question")
        btn = [b for b in at.button if b.label == "Generate Grounded Analysis"][0]
        btn.click().run()
        self.assertTrue(mock_analyze.called)
        self.assertEqual(mock_analyze.call_args.args[0], "custom question")
        self.assertTrue(any("MANUAL_OK" in getattr(m, "value", "") for m in at.markdown))

    @patch("reasoning.analyze")
    def test_rapid_interactions(self, mock_analyze):
        mock_analyze.return_value = {"answer": "RAPID_OK", "sources": [], "confidence": "High"}
        at = self._run()
        for q in EXAMPLES:
            btn = [b for b in at.button if b.label == q][0]
            btn.click().run()
            at = AppTest.from_file(APP_PATH)
            at.run(timeout=60)
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
