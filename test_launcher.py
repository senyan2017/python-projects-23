#!/usr/bin/env python3
"""Minimal verification for launcher.py.

Run it with either:

    python test_launcher.py
    python -m pytest test_launcher.py

It checks the three critical paths without ever spawning an interactive
program: the root entry point, project discovery, and direct launch.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest

import launcher

ROOT = os.path.dirname(os.path.abspath(__file__))


def run_cli(*args: str, stdin: int | None = subprocess.DEVNULL):
    """Invoke launcher.py as a subprocess and capture its result."""
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "launcher.py"), *args],
        cwd=ROOT, stdin=stdin, capture_output=True, text=True, timeout=60,
    )


class CatalogTests(unittest.TestCase):
    def test_catalog_not_empty(self):
        self.assertTrue(launcher.PROJECTS)

    def test_keys_are_unique(self):
        keys = [p.key for p in launcher.PROJECTS]
        self.assertEqual(len(keys), len(set(keys)), "duplicate project keys")

    def test_every_entry_file_exists(self):
        # Project discovery integrity: every catalog entry resolves to a file.
        for p in launcher.PROJECTS:
            self.assertTrue(
                launcher.entry_exists(p),
                f"missing entry for '{p.key}': {launcher.entry_path(p)}",
            )

    def test_discover_reports_no_missing(self):
        report = launcher.discover()
        self.assertEqual(report["missing"], [], "discover() found missing entries")
        self.assertEqual(len(report["ok"]), len(launcher.PROJECTS))


class StatusTests(unittest.TestCase):
    def test_notebooks_flagged_as_notebook(self):
        for p in launcher.PROJECTS:
            if p.kind == launcher.NOTEBOOK:
                tag, _ = launcher.status(p)
                self.assertEqual(tag, "notebook")
                self.assertIsNone(launcher.build_command(p))

    def test_runnable_command_shape(self):
        for p in launcher.PROJECTS:
            if p.kind != launcher.NOTEBOOK:
                cmd = launcher.build_command(p)
                self.assertEqual(cmd, [sys.executable, p.entry])


class RootEntryTests(unittest.TestCase):
    def test_list_runs_and_lists_projects(self):
        result = run_cli("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Todo App", result.stdout)
        self.assertIn("todo", result.stdout)

    def test_interactive_handles_eof_without_hanging(self):
        # No args + closed stdin: the menu should reach EOF and exit cleanly.
        result = run_cli(stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 0, result.stderr)


class DirectLaunchTests(unittest.TestCase):
    def test_dry_run_resolves_command(self):
        result = run_cli("morse", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[dry-run] would run:", result.stdout)
        self.assertIn("main.py", result.stdout)
        self.assertIn("Morsecode-project", result.stdout)

    def test_dry_run_works_by_run_flag(self):
        result = run_cli("--run", "todo", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("todo_app", result.stdout)

    def test_notebook_direct_launch_gives_guidance(self):
        result = run_cli("heart", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Jupyter notebook", result.stdout)

    def test_unknown_key_fails_cleanly(self):
        result = run_cli("does-not-exist")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown project key", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
