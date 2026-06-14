import os
import sys

# Make the repo-root "common" package importable when run as `python main.py`
# from inside this directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.menu import run_menu, MenuExit
from common.storage import JSONStorage
from todo_list import ToDoList


def display_tasks(todo_list):
    tasks = todo_list.list_tasks()
    if not tasks:
        print("No tasks found!")
        return
    print("\nTo-Do List:")
    for idx, task in enumerate(tasks):
        status = "✔" if task["completed"] else "✘"
        print(f"{idx + 1}. {task['description']} [{status}]")


def main():
    storage = JSONStorage("tasks.txt", base_dir=os.path.dirname(os.path.abspath(__file__)))
    todo_list = ToDoList()
    todo_list.tasks = storage.load()  # Load tasks from file

    def add_task():
        description = input("Enter task description: ")
        todo_list.add_task(description)
        storage.save(todo_list.tasks)

    def complete_task():
        display_tasks(todo_list)
        try:
            task_index = int(input("Enter task number to mark as complete: ")) - 1
            todo_list.mark_task_completed(task_index)
            storage.save(todo_list.tasks)
        except (ValueError, IndexError):
            print("Invalid task number.")

    def delete_task():
        display_tasks(todo_list)
        try:
            task_index = int(input("Enter task number to delete: ")) - 1
            todo_list.delete_task(task_index)
            storage.save(todo_list.tasks)
        except (ValueError, IndexError):
            print("Invalid task number.")

    def exit_app():
        print("Exiting To-Do List Application. Goodbye!")
        raise MenuExit

    run_menu("To-Do List Application", [
        ("View tasks", lambda: display_tasks(todo_list)),
        ("Add a task", add_task),
        ("Mark task as completed", complete_task),
        ("Delete a task", delete_task),
        ("Exit", exit_app),
    ])


if __name__ == "__main__":
    main()
