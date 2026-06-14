import json
import os

# Anchor the data file next to this module so the location is stable no matter
# what the current working directory is when the app is launched.
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.txt")


def _normalize_task(raw):
    """Return a valid task dict, or None if the record can't be salvaged."""
    if not isinstance(raw, dict):
        return None
    description = raw.get("description")
    if not isinstance(description, str) or not description.strip():
        return None
    return {"description": description.strip(), "completed": bool(raw.get("completed", False))}


def load_tasks(file_path=None):
    """Load tasks from disk, tolerating missing, empty or corrupt files."""
    if file_path is None:
        file_path = DEFAULT_FILE
    try:
        with open(file_path, "r") as file:
            content = file.read().strip()
    except FileNotFoundError:
        return []

    if not content:
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print(f"Warning: '{file_path}' is corrupted and could not be read. "
              "Starting with an empty list.")
        return []

    if not isinstance(data, list):
        print(f"Warning: '{file_path}' has an unexpected format. "
              "Starting with an empty list.")
        return []

    tasks = []
    for raw in data:
        task = _normalize_task(raw)
        if task is not None:
            tasks.append(task)
    return tasks


def save_tasks(tasks, file_path=None):
    """Persist tasks to disk as JSON."""
    if file_path is None:
        file_path = DEFAULT_FILE
    with open(file_path, "w") as file:
        json.dump(tasks, file, indent=2)
