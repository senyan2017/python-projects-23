#!/usr/bin/env python3
"""Root launcher for the python-projects collection.

Run from the repository root to pick and start any project, either through an
interactive menu or directly by key:

    python launcher.py                 # interactive menu
    python launcher.py --list          # list every project + status
    python launcher.py todo            # launch a project directly by key
    python launcher.py todo --dry-run  # show what would run, without running it

Each project keeps its own folder and stays runnable on its own; this launcher
only discovers the projects and shells out to their existing entry files.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.abspath(__file__))

# Run kinds -----------------------------------------------------------------
CLI = "cli"          # console program, safe to run with `python entry`
GUI = "gui"          # opens a window (pygame/turtle/tkinter), needs a display
SCRIPT = "script"    # one-shot script, usually heavy deps / external hardware
NOTEBOOK = "notebook"  # Jupyter notebook, cannot be run with `python entry`


@dataclass(frozen=True)
class Project:
    key: str            # short, stable, lowercase identifier used on the CLI
    name: str           # human readable name
    directory: str      # folder name under the repo root
    entry: str          # entry file inside the folder
    kind: str           # one of CLI / GUI / SCRIPT / NOTEBOOK
    description: str     # one-line purpose
    requires: tuple = ()  # importable modules needed to actually run it
    note: str = ""       # extra environment caveats (display, hardware, ...)


# Curated catalog. The metadata here (purpose, kind, deps, caveats) cannot be
# derived from folder names alone, which is the whole point of the launcher.
PROJECTS: list[Project] = [
    Project("snake", "AI Snake Game", "AI Snake Game", "main.py", GUI,
            "Snake game rendered with pygame.",
            requires=("pygame", "numpy"), note="Opens a game window (needs a display)."),
    Project("car", "Car Command Game", "Car-game-project", "main.py", CLI,
            "Text command loop: start/stop/help a virtual car."),
    Project("bmi", "Check Your Weight", "Check-your-weight-project", "main.py", CLI,
            "Convert weight between Lbs and Kg from input."),
    Project("expense", "Expense Tracker", "expense_tracker_project", "main.py", CLI,
            "Console expense tracker (saves expenses.txt in its folder)."),
    Project("gif", "GIF Generator", "gif_generator", "main.py", SCRIPT,
            "Generate GIFs using Pillow/torch/transformers.",
            requires=("PIL", "torch", "transformers"),
            note="Heavy ML dependencies and model downloads."),
    Project("hangman", "Hangman Game", "hagman-game-project", "Hangman-Game.py", CLI,
            "Classic word-guessing Hangman in the console."),
    Project("heart", "Heart Disease Prediction", "Heart-disease-prediction-project",
            "main.ipynb", NOTEBOOK,
            "ML notebook predicting heart disease.",
            requires=("pandas", "numpy", "seaborn", "matplotlib")),
    Project("life", "Game of Life", "life-game", "main.py", GUI,
            "Conway's Game of Life rendered with pygame.",
            requires=("pygame", "numpy"), note="Opens a game window (needs a display)."),
    Project("loan", "Loan Price Predictor", "LoanPricePredictor", "main.ipynb", NOTEBOOK,
            "PySpark notebook for loan price prediction.",
            requires=("pyspark", "pandas")),
    Project("morse", "Morse Code", "Morsecode-project", "main.py", CLI,
            "Encode/decode Morse code in the console."),
    Project("music", "Music Playlist Generator", "Music-Playlist-Generator",
            "main.ipynb", NOTEBOOK,
            "Notebook clustering tracks into playlists.",
            requires=("pandas", "sklearn")),
    Project("object-detection", "Object Detection", "object-detection", "main.py", SCRIPT,
            "Real-time YOLO object detection from a webcam.",
            requires=("ultralytics", "cv2"),
            note="Needs a webcam and downloads a YOLO model."),
    Project("pattern", "Pattern Printer", "Pattern", "main.py", CLI,
            "Print a set of ASCII patterns."),
    Project("ocr", "Python OCR", "Python-OCR", "main.py", CLI,
            "OCR text from an image and read it aloud.",
            requires=("cv2", "pytesseract", "pyttsx3"),
            note="Also needs the Tesseract binary installed on the system."),
    Project("shape", "Shape Drawing", "Shape-project", "main.py", GUI,
            "Draw spirograph-style shapes with turtle.",
            requires=("tkinter",), note="Turtle graphics window (needs a display)."),
    Project("tictactoe", "Tic-Tac-Toe", "Tic-Tac-Toe-project", "main.py", CLI,
            "Two-player console Tic-Tac-Toe."),
    Project("todo", "Todo App", "todo_app", "main.py", CLI,
            "Console todo list (saves tasks.txt in its folder)."),
    Project("youtube", "YouTube Downloader", "Youtube-video-downloader-project",
            "main.py", GUI,
            "Tkinter GUI to download YouTube videos.",
            requires=("pytube",), note="Opens a Tkinter window (needs a display)."),
]

PROJECTS_BY_KEY = {p.key: p for p in PROJECTS}


# Filesystem / dependency helpers ------------------------------------------
def project_dir(p: Project) -> str:
    return os.path.join(ROOT, p.directory)


def entry_path(p: Project) -> str:
    return os.path.join(project_dir(p), p.entry)


def entry_exists(p: Project) -> bool:
    return os.path.isfile(entry_path(p))


def requirements_file(p: Project) -> str | None:
    """Return the project's requirements file (the repo mixes .txt and .py)."""
    for name in ("requirements.txt", "requirements.py"):
        candidate = os.path.join(project_dir(p), name)
        if os.path.isfile(candidate):
            return candidate
    return None


def missing_requirements(p: Project) -> list[str]:
    """Modules in `requires` that are not importable in this environment."""
    missing = []
    for module in p.requires:
        try:
            found = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing.append(module)
    return missing


def status(p: Project) -> tuple[str, str]:
    """Return (tag, detail) describing whether the project is ready to run."""
    if not entry_exists(p):
        return "missing", f"entry file not found: {p.entry}"
    if p.kind == NOTEBOOK:
        return "notebook", "open with Jupyter (not directly runnable)"
    missing = missing_requirements(p)
    if missing:
        return "needs deps", "missing: " + ", ".join(missing)
    if p.kind in (GUI, SCRIPT) and p.note:
        return "ready*", p.note
    return "ready", ""


# Discovery -----------------------------------------------------------------
def discover() -> dict[str, list]:
    """Validate the catalog against the filesystem.

    Returns a dict with three lists: catalog entries that resolve to a real
    file (``ok``), catalog entries whose folder/entry is missing (``missing``),
    and project-looking folders on disk that are not in the catalog
    (``uncatalogued``) so newly contributed projects get noticed.
    """
    ok, missing = [], []
    for p in PROJECTS:
        (ok if entry_exists(p) else missing).append(p)

    known_dirs = {p.directory for p in PROJECTS}
    uncatalogued = []
    for name in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, name)
        if not os.path.isdir(full) or name.startswith(".") or name in known_dirs:
            continue
        has_entry = any(
            os.path.isfile(os.path.join(full, f))
            for f in ("main.py", "main.ipynb")
        ) or any(f.endswith((".py", ".ipynb")) for f in os.listdir(full))
        if has_entry:
            uncatalogued.append(name)
    return {"ok": ok, "missing": missing, "uncatalogued": uncatalogued}


# Running -------------------------------------------------------------------
def build_command(p: Project) -> list[str] | None:
    """The argv that would launch the project, or None for notebooks."""
    if p.kind == NOTEBOOK:
        return None
    return [sys.executable, p.entry]


def _notebook_guidance(p: Project) -> str:
    return (
        f"'{p.name}' is a Jupyter notebook and cannot be run with python directly.\n"
        f"  Open it with:  jupyter notebook \"{entry_path(p)}\"\n"
        f"            or:  jupyter lab \"{entry_path(p)}\""
    )


def run_project(p: Project, dry_run: bool = False) -> int:
    """Launch a project. Returns a process-style exit code.

    Handles the awkward cases up front so selecting a project never just
    crashes: missing files, notebooks, and missing dependencies all produce a
    clear message instead of a traceback.
    """
    if not entry_exists(p):
        print(f"Cannot start '{p.name}': entry file not found at {entry_path(p)}")
        return 2

    if p.kind == NOTEBOOK:
        print(_notebook_guidance(p))
        return 0

    missing = missing_requirements(p)
    if missing:
        print(f"Cannot start '{p.name}': missing dependencies: {', '.join(missing)}")
        req = requirements_file(p)
        if req:
            print(f"  Install them first, e.g.:  pip install -r \"{req}\"")
        if p.note:
            print(f"  Note: {p.note}")
        return 1

    command = build_command(p)
    cwd = project_dir(p)
    if dry_run:
        printable = " ".join(command)
        print(f"[dry-run] would run: {printable}")
        print(f"[dry-run] in directory: {cwd}")
        return 0

    if p.note:
        print(f"Note: {p.note}")
    print(f"Launching {p.name} ...  (Ctrl-C to stop)\n")
    try:
        result = subprocess.run(command, cwd=cwd)
        return result.returncode
    except FileNotFoundError:
        print(f"Could not run '{p.name}': {sys.executable} or {p.entry} not found.")
        return 2
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130


# Presentation --------------------------------------------------------------
def _print_warnings(report: dict[str, list]) -> None:
    for p in report["missing"]:
        print(f"  ! catalog entry '{p.key}' points at a missing file ({p.directory}/{p.entry})")
    for name in report["uncatalogued"]:
        print(f"  ? found an uncatalogued project folder: {name}")
    if report["missing"] or report["uncatalogued"]:
        print()


def print_list(report: dict[str, list] | None = None) -> None:
    report = report or discover()
    print("Available projects (run with: python launcher.py <key>)\n")
    print(f"  {'#':>2}  {'KEY':<16} {'KIND':<9} {'STATUS':<10} NAME")
    print(f"  {'-'*2}  {'-'*16} {'-'*9} {'-'*10} {'-'*4}")
    for i, p in enumerate(PROJECTS, 1):
        tag, _ = status(p)
        print(f"  {i:>2}  {p.key:<16} {p.kind:<9} {tag:<10} {p.name}")
    print("\n  ready* = runs, but needs a display / extra environment (see details).")
    _print_warnings(report)


def print_detail(p: Project) -> None:
    tag, detail = status(p)
    print(f"\n{p.name}  [{p.key}]")
    print(f"  Purpose : {p.description}")
    print(f"  Kind    : {p.kind}")
    print(f"  Entry   : {p.directory}/{p.entry}")
    print(f"  Status  : {tag}" + (f" ({detail})" if detail else ""))
    if p.requires:
        print(f"  Needs   : {', '.join(p.requires)}")
    if p.note:
        print(f"  Note    : {p.note}")
    if p.kind == NOTEBOOK:
        print(f"  Run it  : cd \"{p.directory}\" && jupyter notebook {p.entry}")
    else:
        print(f"  Run it  : cd \"{p.directory}\" && python {p.entry}")


# Interactive menu ----------------------------------------------------------
_QUIT_WORDS = {"q", "quit", "exit"}
_BACK_WORDS = {"b", "back"}
_EOF = object()


def _prompt(message: str) -> object:
    """input() that returns the _EOF sentinel instead of crashing on EOF."""
    try:
        return input(message).strip()
    except EOFError:
        return _EOF


def _project_menu(p: Project) -> str:
    """Detail view for one project. Returns 'back' or 'quit'."""
    while True:
        print_detail(p)
        choice = _prompt("\n[r]un, [b]ack, [q]uit: ")
        if choice is _EOF:
            return "quit"
        choice = choice.lower()
        if choice in _QUIT_WORDS:
            return "quit"
        if choice in _BACK_WORDS or choice == "":
            return "back"
        if choice in {"r", "run"}:
            print()
            run_project(p)
            print()
            return "back"
        print("  Please choose r, b, or q.")


def interactive() -> int:
    report = discover()
    print("=" * 60)
    print(" python-projects launcher")
    print("=" * 60)
    while True:
        print()
        print_list(report)
        choice = _prompt("\nSelect a project number or key ('q' to quit): ")
        if choice is _EOF:
            print("\nBye.")
            return 0
        if choice == "":
            continue
        lowered = choice.lower()
        if lowered in _QUIT_WORDS:
            print("Bye.")
            return 0

        project = None
        if lowered in PROJECTS_BY_KEY:
            project = PROJECTS_BY_KEY[lowered]
        elif choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(PROJECTS):
                project = PROJECTS[index - 1]

        if project is None:
            print(f"  '{choice}' is not a valid number or key. Try again.")
            continue

        if _project_menu(project) == "quit":
            print("Bye.")
            return 0


# CLI -----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="launcher.py",
        description="Pick and launch any project in this repository.",
    )
    parser.add_argument(
        "project", nargs="?",
        help="project key (see --list) to launch directly; omit for the menu",
    )
    parser.add_argument("-l", "--list", action="store_true",
                        help="list all projects with their status and exit")
    parser.add_argument("--run", metavar="KEY",
                        help="launch the given project key directly")
    parser.add_argument("--dry-run", action="store_true",
                        help="with a project key, show the command instead of running it")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print_list()
        return 0

    key = args.run or args.project
    if key:
        project = PROJECTS_BY_KEY.get(key.lower())
        if project is None:
            print(f"Unknown project key: {key!r}")
            print("Use 'python launcher.py --list' to see valid keys.")
            return 2
        return run_project(project, dry_run=args.dry_run)

    return interactive()


if __name__ == "__main__":
    raise SystemExit(main())
