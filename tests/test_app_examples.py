import sys
import os
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
        at.run(timeout=30)
        return at

    def test_all_examples_displayed(self):
        at = self._run()
        buttons = [b for b in at.button if b.label in EXAMPLES]
        self.assertEqual(len(buttons), 4)

    @patch("reasoning.analyze")
    def test_click_example_submits_correct_question(self, mock_analyze):
        mock_analyze.return_value = {"answer": "ok", "sources": [], "confidence": "High"}
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertTrue(mock_analyze.called)
        self.assertEqual(mock_analyze.call_args.args[0], EXAMPLES[0])

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

    @patch("reasoning.analyze")
    def test_api_failure_shows_error(self, mock_analyze):
        mock_analyze.side_effect = RuntimeError("boom")
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertTrue(any("boom" in getattr(e, "value", "") for e in at.error) or any("boom" in getattr(m, "value", "") for m in at.markdown))

    @patch("reasoning.analyze")
    def test_empty_answer_handled(self, mock_analyze):
        mock_analyze.return_value = {"answer": "", "sources": [], "confidence": "Low"}
        at = self._run()
        btn = [b for b in at.button if b.label == EXAMPLES[0]][0]
        btn.click().run()
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
