"""
Unit tests for the Diary Entry Application.
"""

import sys
import os
from datetime import date
import unittest

# Ensure src/ is in the python path to import the module
src_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")
)
sys.path.insert(0, src_path)

from diary import (
    validate_date_string,
    parse_search_query,
    serialize_entry,
    deserialize_line,
)


class TestDiaryApplication(unittest.TestCase):

    def test_validate_date_string(self):
        """Test validation of correct and incorrect date input strings."""
        # Valid
        self.assertEqual(validate_date_string("06/19/2026"), date(2026, 6, 19))
        self.assertEqual(validate_date_string("02/29/2020"), date(2020, 2, 29))
        
        # Invalid format syntax
        for fmt in ["06-19-2026", "6/19/2026", "06/19/26", "2026/06/19"]:
            with self.subTest(fmt=fmt):
                with self.assertRaises(ValueError) as ctx:
                    validate_date_string(fmt)
                self.assertIn("Invalid format", str(ctx.exception))

        # Invalid date values
        for val in ["02/29/2021", "13/01/2026", "06/31/2026", "00/12/2026"]:
            with self.subTest(val=val):
                with self.assertRaises(ValueError) as ctx:
                    validate_date_string(val)
                self.assertIn("Invalid date values", str(ctx.exception))

        # Year boundaries (1900 to 2100)
        with self.assertRaises(ValueError) as ctx:
            validate_date_string("12/31/1899")
        self.assertIn("Year must be between", str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            validate_date_string("01/01/2101")
        self.assertIn("Year must be between", str(ctx.exception))

    def test_parse_search_query(self):
        """Test parsing of search queries into YYYY, YYYY-MM, or YYYY-MM-DD formats."""
        # Full date
        self.assertEqual(parse_search_query("06/19/2026"), "2026-06-19")
        # Month-Year
        self.assertEqual(parse_search_query("06/2026"), "2026-06")
        # Year only
        self.assertEqual(parse_search_query("2026"), "2026")

        # Invalid formats
        for bad_query in ["06-2026", "6/2026", "20266", "06/19/26", "13/2026"]:
            with self.subTest(bad_query=bad_query):
                with self.assertRaises(ValueError):
                    parse_search_query(bad_query)

    def test_serialization_and_deserialization(self):
        """Test that entries are correctly serialized to single lines and restored."""
        test_date = date(2026, 6, 4)
        single_line_text = "Today was a fantastic day pairing with Antigravity!"
        
        # Test basic line
        serialized = serialize_entry(test_date, single_line_text)
        self.assertEqual(serialized, "2026-06-04 | Today was a fantastic day pairing with Antigravity!")
        
        date_str, text = deserialize_line(serialized)
        self.assertEqual(date_str, "2026-06-04")
        self.assertEqual(text, single_line_text)

    def test_multiline_serialization(self):
        """Test that multi-line entry text is stored as a single line and successfully restored."""
        test_date = date(2026, 6, 19)
        multiline_text = "Line 1: Started writing the diary application.\nLine 2: Wrote unit tests.\nLine 3: Everything works!"
        
        serialized = serialize_entry(test_date, multiline_text)
        # Verify no actual newline characters exist in the serialized line
        self.assertNotIn("\n", serialized)
        self.assertIn("\\n", serialized)
        
        date_str, text = deserialize_line(serialized)
        self.assertEqual(date_str, "2026-06-19")
        self.assertEqual(text, multiline_text)  # Original newlines are restored


if __name__ == "__main__":
    unittest.main()
