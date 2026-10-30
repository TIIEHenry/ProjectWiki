"""Acceptance examples for the documented title contract."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from title import normalize_title


class TitleAcceptanceTests(unittest.TestCase):
    def test_preserves_content_after_trimming(self):
        """NB-01.1"""
        self.assertEqual(normalize_title("  项目 记录  "), "项目 记录")

    def test_rejects_whitespace_only(self):
        """NB-01.2"""
        with self.assertRaisesRegex(ValueError, "^title is empty$"):
            normalize_title(" \t\n")

    def test_accepts_sixty_codepoints(self):
        """NB-01.3"""
        self.assertEqual(normalize_title("记" * 60), "记" * 60)

    def test_rejects_excess_instead_of_truncating(self):
        """NB-01.4"""
        with self.assertRaisesRegex(ValueError, "^title is too long$"):
            normalize_title("记" * 61)

    def test_keeps_internal_newlines_under_current_contract(self):
        """NB-01.1"""
        self.assertEqual(normalize_title("one\ntwo"), "one\ntwo")


if __name__ == "__main__":
    unittest.main()
