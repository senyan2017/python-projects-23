import json
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE_PATH = os.path.join(_BASE_DIR, "tasks.txt")


def load_tasks(file_path=None):
    """Load tasks from a JSON file.

    Returns a list of task dicts.  Handles missing files, empty files,
    corrupt JSON, and data that is not a list by returning an empty list
    and printing a warning when appropriate.
    """
    if file_path is None:
        file_path = DEFAULT_FILE_PATH
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return []
            tasks = json.loads(content)
            if not isinstance(tasks, list):
                print(f"Warning: data in '{file_path}' is not a list, starting with empty task list.")
                return []
            # Validate each task has the expected structure
            validated = []
            for item in tasks:
                if isinstance(item, dict) and "description" in item:
                    validated.append({
                        "description": str(item["description"]),
                        "completed": bool(item.get("completed", False)),
                    })
                # Silently skip malformed entries
            return validated
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: '{file_path}' contains invalid JSON, starting with empty task list.")
        return []
    except Exception as e:
        print(f"Warning: failed to load tasks from '{file_path}': {e}")
        return []


def save_tasks(tasks, file_path=None):
    """Save the task list to a JSON file."""
    if file_path is None:
        file_path = DEFAULT_FILE_PATH
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
