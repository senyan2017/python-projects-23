"""Minimal tests for expense_tracker_project: input validation, data save/reload, edge cases."""
import json
import os
import sys
import tempfile
import unittest

# Ensure the expense_tracker_project package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from expense_manager import ExpenseManager
import file_manager


class TestExpenseManager(unittest.TestCase):
    """Tests for ExpenseManager business logic."""

    def setUp(self):
        self.em = ExpenseManager()

    # -- add_expense --------------------------------------------------------

    def test_add_expense_normal(self):
        result = self.em.add_expense(25.50, "Food", "Lunch")
        self.assertIs(result, True)
        self.assertEqual(len(self.em.expenses), 1)
        self.assertAlmostEqual(self.em.expenses[0]["amount"], 25.50)
        self.assertEqual(self.em.expenses[0]["category"], "Food")
        self.assertEqual(self.em.expenses[0]["description"], "Lunch")

    def test_add_expense_string_amount(self):
        result = self.em.add_expense("abc", "Food", "Lunch")
        self.assertIsInstance(result, str)

    def test_add_expense_negative_amount(self):
        result = self.em.add_expense(-10, "Food", "Lunch")
        self.assertIsInstance(result, str)

    def test_add_expense_zero_amount(self):
        result = self.em.add_expense(0, "Food", "Lunch")
        self.assertIsInstance(result, str)

    def test_add_expense_empty_category(self):
        result = self.em.add_expense(10, "", "Lunch")
        self.assertIsInstance(result, str)

    def test_add_expense_whitespace_category(self):
        result = self.em.add_expense(10, "   ", "Lunch")
        self.assertIsInstance(result, str)

    def test_add_expense_empty_description_gets_default(self):
        result = self.em.add_expense(10, "Food", "")
        self.assertIs(result, True)
        self.assertEqual(self.em.expenses[0]["description"], "(no description)")

    def test_add_expense_none_description(self):
        result = self.em.add_expense(10, "Food", None)
        self.assertIs(result, True)

    # -- get_summary --------------------------------------------------------

    def test_summary_empty(self):
        summary = self.em.get_summary()
        self.assertEqual(summary, {})

    def test_summary_aggregation(self):
        self.em.add_expense(10, "Food", "a")
        self.em.add_expense(20, "Food", "b")
        self.em.add_expense(15, "Transport", "c")
        summary = self.em.get_summary()
        self.assertAlmostEqual(summary["Food"], 30.0)
        self.assertAlmostEqual(summary["Transport"], 15.0)

    def test_summary_handles_string_amount_in_raw_data(self):
        """If raw data contains string amounts, summary should skip them."""
        self.em.expenses = [
            {"amount": "bad", "category": "Food", "description": "x"},
            {"amount": 10, "category": "Food", "description": "y"},
        ]
        summary = self.em.get_summary()
        self.assertAlmostEqual(summary["Food"], 10.0)


class TestFileManager(unittest.TestCase):
    """Tests for file_manager save/load round-trip and corrupt data handling."""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, dir=os.path.dirname(os.path.abspath(__file__))
        )
        self.tmpfile.close()
        self.path = self.tmpfile.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_save_and_reload(self):
        expenses = [
            {"amount": 25.5, "category": "Food", "description": "Lunch"},
            {"amount": 10.0, "category": "Transport", "description": "Bus"},
        ]
        file_manager.save_expenses(expenses, self.path)
        loaded = file_manager.load_expenses(self.path)
        self.assertEqual(loaded, expenses)

    def test_load_missing_file(self):
        result = file_manager.load_expenses("/tmp/nonexistent_expense_file_12345.txt")
        self.assertEqual(result, [])

    def test_load_empty_file(self):
        with open(self.path, "w") as f:
            f.write("")
        result = file_manager.load_expenses(self.path)
        self.assertEqual(result, [])

    def test_load_invalid_json(self):
        with open(self.path, "w") as f:
            f.write("not json at all!!!")
        result = file_manager.load_expenses(self.path)
        self.assertEqual(result, [])

    def test_load_not_a_list(self):
        with open(self.path, "w") as f:
            json.dump({"key": "value"}, f)
        result = file_manager.load_expenses(self.path)
        self.assertEqual(result, [])

    def test_load_malformed_entries_skipped(self):
        data = [
            {"amount": 10, "category": "Food", "description": "ok"},
            "just a string",
            {"amount": "bad", "category": "Food", "description": "bad amount"},
            {"category": "Food"},  # missing amount
            {"amount": 20, "category": "Transport", "description": "ok2"},
        ]
        with open(self.path, "w") as f:
            json.dump(data, f)
        result = file_manager.load_expenses(self.path)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0]["amount"], 10.0)
        self.assertAlmostEqual(result[1]["amount"], 20.0)

    def test_load_empty_category_becomes_uncategorized(self):
        data = [{"amount": 5, "category": "", "description": "x"}]
        with open(self.path, "w") as f:
            json.dump(data, f)
        result = file_manager.load_expenses(self.path)
        self.assertEqual(result[0]["category"], "Uncategorized")

    def test_default_path_is_absolute(self):
        """Verify that the default file path is absolute (not CWD-dependent)."""
        self.assertTrue(os.path.isabs(file_manager.DEFAULT_FILE_PATH))


if __name__ == "__main__":
    unittest.main()
