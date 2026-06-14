import os
import sys

# Make the repo-root "common" package importable when run as `python main.py`
# from inside this directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.menu import run_menu, MenuExit
from common.storage import JSONStorage
from expense_manager import ExpenseManager


def display_expenses(expense_manager):
    expenses = expense_manager.list_expenses()
    if not expenses:
        print("No expenses recorded!")
        return
    print("\nList of Expenses:")
    for idx, expense in enumerate(expenses, 1):
        print(f"{idx}. ${expense['amount']} - {expense['category']} - {expense['description']}")


def display_summary(expense_manager):
    summary = expense_manager.get_summary()
    if not summary:
        print("No expenses recorded!")
        return
    print("\nExpense Summary by Category:")
    for category, total in summary.items():
        print(f"{category}: ${total:.2f}")


def main():
    storage = JSONStorage("expenses.txt", base_dir=os.path.dirname(os.path.abspath(__file__)))
    expense_manager = ExpenseManager()
    expense_manager.expenses = storage.load()  # Load existing expenses

    def add_expense():
        try:
            amount = float(input("Enter amount: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            return
        category = input("Enter category (e.g., Food, Transport): ")
        description = input("Enter description: ")
        expense_manager.add_expense(amount, category, description)
        storage.save(expense_manager.expenses)
        print("Expense added successfully!")

    def exit_app():
        print("Exiting Expense Tracker. Goodbye!")
        raise MenuExit

    run_menu("Personal Expense Tracker", [
        ("Add an expense", add_expense),
        ("View expenses", lambda: display_expenses(expense_manager)),
        ("View summary by category", lambda: display_summary(expense_manager)),
        ("Exit", exit_app),
    ])


if __name__ == "__main__":
    main()
