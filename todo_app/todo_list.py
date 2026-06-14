class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        """Add a new task to the list.

        Returns True on success, or an error message string on failure.
        """
        if not description or not description.strip():
            return "Task description cannot be empty."
        task = {"description": description.strip(), "completed": False}
        self.tasks.append(task)
        return True

    def mark_task_completed(self, task_number):
        """Mark a task as completed by its 1-based task number.

        Returns True on success, or an error message string on failure.
        """
        if not self.tasks:
            return "No tasks available."
        if not isinstance(task_number, int):
            return "Task number must be an integer."
        if task_number < 1 or task_number > len(self.tasks):
            return f"Invalid task number. Please enter a number between 1 and {len(self.tasks)}."
        task = self.tasks[task_number - 1]
        if task["completed"]:
            return f"Task {task_number} is already completed."
        task["completed"] = True
        return True

    def delete_task(self, task_number):
        """Delete a task by its 1-based task number.

        Returns True on success, or an error message string on failure.
        """
        if not self.tasks:
            return "No tasks available."
        if not isinstance(task_number, int):
            return "Task number must be an integer."
        if task_number < 1 or task_number > len(self.tasks):
            return f"Invalid task number. Please enter a number between 1 and {len(self.tasks)}."
        self.tasks.pop(task_number - 1)
        return True

    def list_tasks(self):
        """Return the list of tasks."""
        return self.tasks
