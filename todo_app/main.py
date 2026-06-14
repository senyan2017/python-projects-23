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
            description = input("Enter task description: ").strip()
            result = todo_list.add_task(description)
            if result is True:
                file_manager.save_tasks(todo_list.tasks)
                print("Task added successfully!")
            else:
                print(result)
        elif choice == "3":
            display_tasks(todo_list)
            if not todo_list.list_tasks():
                continue
            raw = input("Enter task number to mark as complete: ").strip()
            try:
                task_number = int(raw)
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            result = todo_list.mark_task_completed(task_number)
            if result is True:
                file_manager.save_tasks(todo_list.tasks)
                print(f"Task {task_number} marked as completed!")
            else:
                print(result)
        elif choice == "4":
            display_tasks(todo_list)
            if not todo_list.list_tasks():
                continue
            raw = input("Enter task number to delete: ").strip()
            try:
                task_number = int(raw)
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            result = todo_list.delete_task(task_number)
            if result is True:
                file_manager.save_tasks(todo_list.tasks)
                print(f"Task {task_number} deleted!")
            else:
                print(result)
        elif choice == "5":
            print("Exiting To-Do List Application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
