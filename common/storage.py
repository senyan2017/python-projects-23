import json
import os


class JsonStore:
    """Simple JSON file storage for list-based data.

    Handles loading and saving a JSON list to a file, with
    FileNotFoundError handled gracefully (returns empty list).
    """

    def __init__(self, filename, data_dir=None):
        if data_dir is None:
            data_dir = "."
        self.file_path = os.path.join(data_dir, filename)

    def load(self):
        """Load and return a list from the JSON file, or [] if not found / corrupt."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Warning: {self.file_path} is corrupted, starting fresh.")
            return []

    def save(self, data):
        """Save a list to the JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Error saving data: {e}")
