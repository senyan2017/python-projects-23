"""Minimal tests for todo_app: input validation, data save/reload, edge cases."""
import json
import os
import sys
import tempfile
import unittest

# Ensure the todo_app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from todo_list import ToDoList
import file_manager


class TestToDoList(unittest.TestCase):
    """Tests for ToDoList business logic."""

    def setUp(self):
        self.tdl = ToDoList()

    # -- add_task -----------------------------------------------------------

    def test_add_task_normal(self):
        result = self.tdl.add_task("Buy milk")
        self.assertIs(result, True)
        self.assertEqual(len(self.tdl.tasks), 1)
        self.assertEqual(self.tdl.tasks[0]["description"], "Buy milk")
        self.assertFalse(self.tdl.tasks[0]["completed"])

    def test_add_task_empty_description(self):
        result = self.tdl.add_task("")
        self.assertIsInstance(result, str)  # error message

    def test_add_task_whitespace_only(self):
        result = self.tdl.add_task("   ")
        self.assertIsInstance(result, str)

    def test_add_task_none(self):
        result = self.tdl.add_task(None)
        self.assertIsInstance(result, str)

    def test_add_task_strips_whitespace(self):
        self.tdl.add_task("  hello  ")
        self.assertEqual(self.tdl.tasks[0]["description"], "hello")

    # -- mark_task_completed ------------------------------------------------

    def test_mark_completed_normal(self):
        self.tdl.add_task("Task A")
        result = self.tdl.mark_task_completed(1)
        self.assertIs(result, True)
        self.assertTrue(self.tdl.tasks[0]["completed"])

    def test_mark_completed_empty_list(self):
        result = self.tdl.mark_task_completed(1)
        self.assertIsInstance(result, str)

    def test_mark_completed_out_of_range(self):
        self.tdl.add_task("Task A")
        result = self.tdl.mark_task_completed(5)
        self.assertIsInstance(result, str)

    def test_mark_completed_zero(self):
        self.tdl.add_task("Task A")
        result = self.tdl.mark_task_completed(0)
        self.assertIsInstance(result, str)

    def test_mark_completed_negative(self):
        self.tdl.add_task("Task A")
        result = self.tdl.mark_task_completed(-1)
        self.assertIsInstance(result, str)

    def test_mark_completed_already_done(self):
        self.tdl.add_task("Task A")
        self.tdl.mark_task_completed(1)
        result = self.tdl.mark_task_completed(1)
        self.assertIsInstance(result, str)  # "already completed"

    def test_mark_completed_not_int(self):
        self.tdl.add_task("Task A")
        result = self.tdl.mark_task_completed("abc")
        self.assertIsInstance(result, str)

    # -- delete_task --------------------------------------------------------

    def test_delete_normal(self):
        self.tdl.add_task("Task A")
        self.tdl.add_task("Task B")
        result = self.tdl.delete_task(1)
        self.assertIs(result, True)
        self.assertEqual(len(self.tdl.tasks), 1)
        self.assertEqual(self.tdl.tasks[0]["description"], "Task B")

    def test_delete_empty_list(self):
        result = self.tdl.delete_task(1)
        self.assertIsInstance(result, str)

    def test_delete_out_of_range(self):
        self.tdl.add_task("Task A")
        result = self.tdl.delete_task(99)
        self.assertIsInstance(result, str)
        self.assertEqual(len(self.tdl.tasks), 1)


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
        tasks = [
            {"description": "Buy milk", "completed": False},
            {"description": "Walk dog", "completed": True},
        ]
        file_manager.save_tasks(tasks, self.path)
        loaded = file_manager.load_tasks(self.path)
        self.assertEqual(loaded, tasks)

    def test_load_missing_file(self):
        result = file_manager.load_tasks("/tmp/nonexistent_todo_file_12345.txt")
        self.assertEqual(result, [])

    def test_load_empty_file(self):
        with open(self.path, "w") as f:
            f.write("")
        result = file_manager.load_tasks(self.path)
        self.assertEqual(result, [])

    def test_load_invalid_json(self):
        with open(self.path, "w") as f:
            f.write("{not valid json!!!")
        result = file_manager.load_tasks(self.path)
        self.assertEqual(result, [])

    def test_load_not_a_list(self):
        with open(self.path, "w") as f:
            json.dump({"key": "value"}, f)
        result = file_manager.load_tasks(self.path)
        self.assertEqual(result, [])

    def test_load_malformed_entries_skipped(self):
        data = [
            {"description": "Good task", "completed": False},
            "just a string",
            42,
            {"no_description_key": True},
            {"description": "Another good task", "completed": True},
        ]
        with open(self.path, "w") as f:
            json.dump(data, f)
        result = file_manager.load_tasks(self.path)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["description"], "Good task")
        self.assertEqual(result[1]["description"], "Another good task")

    def test_default_path_is_absolute(self):
        """Verify that the default file path is absolute (not CWD-dependent)."""
        self.assertTrue(os.path.isabs(file_manager.DEFAULT_FILE_PATH))


if __name__ == "__main__":
    unittest.main()
