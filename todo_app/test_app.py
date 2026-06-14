import json
import os
import sys
import tempfile
import unittest

# Make the local modules importable regardless of the working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import file_manager
from todo_list import ToDoList


class ToDoListTests(unittest.TestCase):
    def test_add_task_rejects_empty(self):
        todo = ToDoList()
        with self.assertRaises(ValueError):
            todo.add_task("   ")
        self.assertEqual(todo.list_tasks(), [])

    def test_add_task_strips_and_stores(self):
        todo = ToDoList()
        todo.add_task("  buy milk  ")
        self.assertEqual(todo.list_tasks()[0]["description"], "buy milk")
        self.assertFalse(todo.list_tasks()[0]["completed"])

    def test_mark_completed_is_idempotent(self):
        todo = ToDoList()
        todo.add_task("task")
        self.assertTrue(todo.mark_task_completed(0))   # newly completed
        self.assertFalse(todo.mark_task_completed(0))  # already completed

    def test_mark_out_of_range_raises(self):
        todo = ToDoList()
        with self.assertRaises(IndexError):
            todo.mark_task_completed(5)

    def test_delete_returns_task_and_validates_range(self):
        todo = ToDoList()
        todo.add_task("task")
        removed = todo.delete_task(0)
        self.assertEqual(removed["description"], "task")
        with self.assertRaises(IndexError):
            todo.delete_task(0)


class FileManagerTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_reload_round_trip(self):
        tasks = [
            {"description": "a", "completed": False},
            {"description": "b", "completed": True},
        ]
        file_manager.save_tasks(tasks, self.path)
        self.assertEqual(file_manager.load_tasks(self.path), tasks)

    def test_load_empty_file(self):
        # mkstemp leaves an empty file behind
        self.assertEqual(file_manager.load_tasks(self.path), [])

    def test_load_corrupt_json(self):
        with open(self.path, "w") as f:
            f.write("{not valid json")
        self.assertEqual(file_manager.load_tasks(self.path), [])

    def test_load_skips_malformed_records(self):
        with open(self.path, "w") as f:
            json.dump(
                [{"description": "ok", "completed": True}, {"oops": 1}, "garbage"],
                f,
            )
        self.assertEqual(
            file_manager.load_tasks(self.path),
            [{"description": "ok", "completed": True}],
        )

    def test_load_missing_file(self):
        os.remove(self.path)
        self.assertEqual(file_manager.load_tasks(self.path), [])


if __name__ == "__main__":
    unittest.main()
