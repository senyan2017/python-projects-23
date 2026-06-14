import json
import os
import sys
import tempfile
import unittest

# Make the local modules importable regardless of the working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import file_manager
from expense_manager import ExpenseManager, parse_amount


class ParseAmountTests(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(parse_amount("12.5"), 12.5)
        self.assertEqual(parse_amount(10), 10.0)

    def test_rejects_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_amount("abc")

    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            parse_amount("-5")

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            parse_amount("0")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            parse_amount("")


class ExpenseManagerTests(unittest.TestCase):
    def test_defaults_for_empty_fields(self):
        mgr = ExpenseManager()
        exp = mgr.add_expense("5", "   ", "")
        self.assertEqual(exp["category"], "Uncategorized")
        self.assertEqual(exp["description"], "No description")

    def test_add_invalid_amount_raises(self):
        mgr = ExpenseManager()
        with self.assertRaises(ValueError):
            mgr.add_expense("-1", "Food", "lunch")

    def test_summary_aggregates_by_category(self):
        mgr = ExpenseManager()
        mgr.add_expense("10", "Food", "a")
        mgr.add_expense("5.5", "Food", "b")
        mgr.add_expense("3", "Transport", "c")
        summary = mgr.get_summary()
        self.assertAlmostEqual(summary["Food"], 15.5)
        self.assertAlmostEqual(summary["Transport"], 3)

    def test_summary_skips_malformed_records(self):
        mgr = ExpenseManager()
        mgr.expenses = [
            {"amount": "oops", "category": "X", "description": "d"},
            {"amount": 4, "category": "Y", "description": "d"},
        ]
        summary = mgr.get_summary()
        self.assertNotIn("X", summary)
        self.assertAlmostEqual(summary["Y"], 4)


class FileManagerTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_reload_round_trip(self):
        mgr = ExpenseManager()
        mgr.add_expense("12.34", "Food", "lunch")
        file_manager.save_expenses(mgr.expenses, self.path)
        self.assertEqual(file_manager.load_expenses(self.path), mgr.expenses)

    def test_load_empty_file(self):
        self.assertEqual(file_manager.load_expenses(self.path), [])

    def test_load_corrupt_json(self):
        with open(self.path, "w") as f:
            f.write("not json!!")
        self.assertEqual(file_manager.load_expenses(self.path), [])

    def test_load_skips_malformed_records(self):
        with open(self.path, "w") as f:
            json.dump(
                [
                    {"amount": 5, "category": "Food", "description": "x"},
                    {"amount": "bad"},
                    123,
                ],
                f,
            )
        self.assertEqual(
            file_manager.load_expenses(self.path),
            [{"amount": 5.0, "category": "Food", "description": "x"}],
        )


if __name__ == "__main__":
    unittest.main()
