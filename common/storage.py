"""Tiny JSON list storage shared by the CLI projects.

Replaces the per-project ``file_manager.py`` modules so the load/save and
path-handling logic only has to be fixed in one place.
"""

import json
import os


class JSONStorage:
    """Load and save a JSON list from a single file.

    The path is resolved relative to ``base_dir`` (the calling project's
    directory) so each project keeps its own data file next to its code,
    no matter which directory the program is launched from.
    """

    def __init__(self, filename, base_dir=None):
        if base_dir is None:
            base_dir = os.getcwd()
        self.path = os.path.join(base_dir, filename)

    def load(self, default=None):
        """Return the stored list, or ``default`` (``[]``) when there is no
        data yet.

        A missing file *or* an empty/whitespace-only file both count as "no
        data yet" so a first run never crashes. A non-empty file with truly
        malformed JSON is still allowed to raise, so real corruption is not
        silently swallowed.
        """
        fallback = [] if default is None else default
        try:
            with open(self.path, "r") as file:
                content = file.read()
        except FileNotFoundError:
            return fallback
        if not content.strip():
            return fallback
        return json.loads(content)

    def save(self, data):
        """Write ``data`` back to disk as JSON."""
        with open(self.path, "w") as file:
            json.dump(data, file)
