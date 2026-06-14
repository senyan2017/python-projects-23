# Personal Expense Tracker

## Overview
This is a command-line Personal Expense Tracker that allows users to:
- Add expenses with category and description
- View a list of all recorded expenses
- View a summary of expenses categorized by type

## Files
- `main.py`: The main script to run the application.
- `expense_manager.py`: Contains the `ExpenseManager` class, which manages expense data.
- `expenses.txt`: Stores expense data persistently.

File I/O and the menu loop are shared with the other CLI projects through
the repo-level `common/` package (`common/storage.py`, `common/menu.py`).

## Usage
Run the application by executing:
```bash
python main.py
```
Follow the on-screen instructions to manage your expenses.
