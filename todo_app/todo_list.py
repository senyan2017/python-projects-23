class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        """Add a new task to the list.

        Raises ValueError if the description is missing or only whitespace.
        """
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Task description cannot be empty.")
        task = {"description": description.strip(), "completed": False}
        self.tasks.append(task)
        return task

    def get_task(self, task_index):
        """Return the task at the given index, or None if out of range."""
        if 0 <= task_index < len(self.tasks):
            return self.tasks[task_index]
        return None

    def mark_task_completed(self, task_index):
        """Mark a task as completed.

        Returns True if it was newly completed, False if it was already
        completed. Raises IndexError if the index is out of range.
        """
        task = self.get_task(task_index)
        if task is None:
            raise IndexError("Task number is out of range.")
        if task["completed"]:
            return False
        task["completed"] = True
        return True

    def delete_task(self, task_index):
        """Delete a task and return it.

        Raises IndexError if the index is out of range.
        """
        if self.get_task(task_index) is None:
            raise IndexError("Task number is out of range.")
        return self.tasks.pop(task_index)

    def list_tasks(self):
        """Return the list of tasks."""
        return self.tasks
