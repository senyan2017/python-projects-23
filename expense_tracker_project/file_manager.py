import json
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE_PATH = os.path.join(_BASE_DIR, "expenses.txt")


def load_expenses(file_path=None):
    """Load expenses from a JSON file.

    Returns a list of expense dicts.  Handles missing files, empty files,
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
            expenses = json.loads(content)
            if not isinstance(expenses, list):
                print(f"Warning: data in '{file_path}' is not a list, starting with empty expense list.")
                return []
            # Validate each expense entry
            validated = []
            for item in expenses:
                if isinstance(item, dict) and "amount" in item and "category" in item:
                    try:
                        amount = float(item["amount"])
                    except (ValueError, TypeError):
                        continue  # skip malformed amount
                    validated.append({
                        "amount": amount,
                        "category": str(item["category"]).strip() or "Uncategorized",
                        "description": str(item.get("description", "")).strip(),
                    })
            return validated
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: '{file_path}' contains invalid JSON, starting with empty expense list.")
        return []
    except Exception as e:
        print(f"Warning: failed to load expenses from '{file_path}': {e}")
        return []


def save_expenses(expenses, file_path=None):
    """Save the expense list to a JSON file."""
    if file_path is None:
        file_path = DEFAULT_FILE_PATH
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(expenses, file, ensure_ascii=False, indent=2)
