import sys
import os

# Allow importing the shared 'common' package from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import JsonStore, Menu, safe_float_input
from expense_manager import ExpenseManager

# Storage lives inside the expense_tracker_project directory
store = JsonStore("expenses.json", data_dir=os.path.dirname(os.path.abspath(__file__)))

MENU_TITLE = "Personal Expense Tracker"
MENU_CHOICES = ["Add an expense", "View expenses", "View summary by category"]


def display_expenses(manager):
    expenses = manager.list_expenses()
    if not expenses:
        print("No expenses recorded!")
        return
    print("\nList of Expenses:")
    for idx, expense in enumerate(expenses, 1):
        print(f"  {idx}. ${expense['amount']:.2f} - {expense['category']} - {expense['description']}")


def display_summary(manager):
    summary = manager.get_summary()
    if not summary:
        print("No expenses recorded!")
        return
    print("\nExpense Summary by Category:")
    for category, total in summary.items():
        print(f"  {category}: ${total:.2f}")


def add_expense(manager):
    amount = safe_float_input("Enter amount: ")
    if amount is None:
        print("Invalid amount.")
        return
    category = input("Enter category (e.g., Food, Transport): ").strip()
    if not category:
        print("Category cannot be empty.")
        return
    description = input("Enter description: ").strip()
    manager.add_expense(amount, category, description)
    store.save(manager.expenses)
    print("Expense added successfully!")


def view_expenses(manager):
    display_expenses(manager)


def view_summary(manager):
    display_summary(manager)


def main():
    manager = ExpenseManager()
    manager.expenses = store.load()

    menu = Menu(MENU_TITLE, MENU_CHOICES)
    handlers = [
        lambda: add_expense(manager),
        lambda: view_expenses(manager),
        lambda: view_summary(manager),
    ]
    menu.run(handlers)


if __name__ == "__main__":
    main()
