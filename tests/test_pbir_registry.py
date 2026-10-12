"""Offline unit tests for defensive Power BI PBIR metadata validation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pbir_registry import validate_pages, validate_query_order


class PagesRegistryTests(unittest.TestCase):
    def test_valid_registry(self):
        self.assertEqual(
            validate_pages({"pageOrder": ["overview", "detail"], "activePageName": "overview"},
                           {"overview", "detail"}),
            [],
        )

    def test_duplicate_missing_and_unlisted_pages_are_reported(self):
        errors = validate_pages(
            {"pageOrder": ["overview", "overview", "absent"], "activePageName": "overview"},
            {"overview", "orphan"},
        )
        self.assertTrue(any("Duplicate PBIR pageOrder" in error for error in errors))
        self.assertTrue(any("Missing PBIR page: absent" in error for error in errors))
        self.assertTrue(any("Unlisted PBIR page file: orphan" in error for error in errors))

    def test_malformed_page_registry_is_a_controlled_error(self):
        for bad in (None, [], {"pageOrder": "overview"}, {"pageOrder": [42]}):
            errors = validate_pages(bad, {"overview"})
            self.assertTrue(errors and "Invalid" in errors[0])

    def test_invalid_active_page_is_reported(self):
        errors = validate_pages(
            {"pageOrder": ["overview"], "activePageName": "other"}, {"overview"}
        )
        self.assertTrue(any("Invalid active PBIR page" in error for error in errors))


class QueryOrderTests(unittest.TestCase):
    def test_valid_query_order(self):
        self.assertEqual(validate_query_order('["dim_players", "fct_transfers"]',
                                              {"dim_players", "fct_transfers"}), [])

    def test_malformed_query_order_json_is_a_controlled_error(self):
        errors = validate_query_order('["dim_players", ]', {"dim_players"})
        self.assertTrue(any("Invalid PBI_QueryOrder JSON" in error for error in errors))

    def test_wrong_query_order_type_is_reported(self):
        errors = validate_query_order('{"name": "dim_players"}', {"dim_players"})
        self.assertTrue(any("expected an array" in error for error in errors))

    def test_stale_and_duplicate_query_tables_are_reported(self):
        errors = validate_query_order('["dim_players", "dim_players", "stale"]',
                                      {"dim_players"})
        self.assertTrue(any("Duplicate PBI_QueryOrder table" in error for error in errors))
        self.assertTrue(any("Stale PBI_QueryOrder table: stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
