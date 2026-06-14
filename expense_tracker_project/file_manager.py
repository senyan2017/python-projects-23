import json
import math
import os

# Anchor the data file next to this module so the location is stable no matter
# what the current working directory is when the app is launched.
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.txt")


def _normalize_expense(raw):
    """Return a valid expense dict, or None if the record can't be salvaged."""
    if not isinstance(raw, dict):
        return None
    try:
        amount = float(raw.get("amount"))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(amount):
        return None

    category = raw.get("category")
    category = category.strip() if isinstance(category, str) and category.strip() else "Uncategorized"

    description = raw.get("description")
    description = description.strip() if isinstance(description, str) and description.strip() else "No description"

    return {"amount": round(amount, 2), "category": category, "description": description}


def load_expenses(file_path=None):
    """Load expenses from disk, tolerating missing, empty or corrupt files."""
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

    expenses = []
    for raw in data:
        expense = _normalize_expense(raw)
        if expense is not None:
            expenses.append(expense)
    return expenses


def save_expenses(expenses, file_path=None):
    """Persist expenses to disk as JSON."""
    if file_path is None:
        file_path = DEFAULT_FILE
    with open(file_path, "w") as file:
        json.dump(expenses, file, indent=2)
