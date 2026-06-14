import sys
import os

# Allow importing the shared 'common' package from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import JsonStore, Menu, safe_int_input
from todo_list import ToDoList

# Storage lives inside the todo_app directory
store = JsonStore("tasks.json", data_dir=os.path.dirname(os.path.abspath(__file__)))

MENU_TITLE = "To-Do List Application"
MENU_CHOICES = ["View tasks", "Add a task", "Mark task as completed", "Delete a task"]


def display_tasks(todo_list):
    tasks = todo_list.list_tasks()
    if not tasks:
        print("No tasks found!")
        return
    print("\nTo-Do List:")
    for idx, task in enumerate(tasks, 1):
        status = "\u2714" if task["completed"] else "\u2718"
        print(f"  {idx}. {task['description']} [{status}]")


def view_tasks(todo_list):
    display_tasks(todo_list)


def add_task(todo_list):
    description = input("Enter task description: ").strip()
    if not description:
        print("Task description cannot be empty.")
        return
    todo_list.add_task(description)
    store.save(todo_list.tasks)
    print("Task added.")


def mark_completed(todo_list):
    display_tasks(todo_list)
    if not todo_list.tasks:
        return
    idx = safe_int_input("Enter task number to mark as complete: ")
    if idx is None:
        print("Invalid task number.")
        return
    idx -= 1
    if 0 <= idx < len(todo_list.tasks):
        todo_list.mark_task_completed(idx)
        store.save(todo_list.tasks)
        print("Task marked as completed.")
    else:
        print("Invalid task number.")


def delete_task(todo_list):
    display_tasks(todo_list)
    if not todo_list.tasks:
        return
    idx = safe_int_input("Enter task number to delete: ")
    if idx is None:
        print("Invalid task number.")
        return
    idx -= 1
    if 0 <= idx < len(todo_list.tasks):
        todo_list.delete_task(idx)
        store.save(todo_list.tasks)
        print("Task deleted.")
    else:
        print("Invalid task number.")


def main():
    todo_list = ToDoList()
    todo_list.tasks = store.load()

    menu = Menu(MENU_TITLE, MENU_CHOICES)
    handlers = [
        lambda: view_tasks(todo_list),
        lambda: add_task(todo_list),
        lambda: mark_completed(todo_list),
        lambda: delete_task(todo_list),
    ]
    menu.run(handlers)


if __name__ == "__main__":
    main()
