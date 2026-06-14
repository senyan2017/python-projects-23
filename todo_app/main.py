from todo_list import ToDoList
import file_manager


def display_tasks(todo_list):
    tasks = todo_list.list_tasks()
    if not tasks:
        print("No tasks found!")
        return
    print("\nTo-Do List:")
    for idx, task in enumerate(tasks, 1):
        status = "✔" if task["completed"] else "✘"
        print(f"{idx}. {task['description']} [{status}]")


def prompt_task_number(prompt):
    """Read a 1-based task number and return a 0-based index, or None if invalid."""
    raw = input(prompt).strip()
    try:
        return int(raw) - 1
    except ValueError:
        print("Invalid task number. Please enter a whole number.")
        return None


def main():
    todo_list = ToDoList()
    todo_list.tasks = file_manager.load_tasks()  # Load tasks from file

    while True:
        print("\nTo-Do List Application")
        print("1. View tasks")
        print("2. Add a task")
        print("3. Mark task as completed")
        print("4. Delete a task")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_tasks(todo_list)
        elif choice == "2":
            description = input("Enter task description: ")
            try:
                todo_list.add_task(description)
            except ValueError as exc:
                print(exc)
                continue
            file_manager.save_tasks(todo_list.tasks)
            print("Task added successfully!")
        elif choice == "3":
            if not todo_list.list_tasks():
                print("No tasks to update yet. Add one first!")
                continue
            display_tasks(todo_list)
            index = prompt_task_number("Enter task number to mark as complete: ")
            if index is None:
                continue
            try:
                newly_completed = todo_list.mark_task_completed(index)
            except IndexError:
                print("Invalid task number.")
                continue
            if newly_completed:
                file_manager.save_tasks(todo_list.tasks)
                print("Task marked as completed!")
            else:
                print("That task is already completed.")
        elif choice == "4":
            if not todo_list.list_tasks():
                print("No tasks to delete yet. Add one first!")
                continue
            display_tasks(todo_list)
            index = prompt_task_number("Enter task number to delete: ")
            if index is None:
                continue
            try:
                removed = todo_list.delete_task(index)
            except IndexError:
                print("Invalid task number.")
                continue
            file_manager.save_tasks(todo_list.tasks)
            print(f"Deleted task: {removed['description']}")
        elif choice == "5":
            print("Exiting To-Do List Application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
