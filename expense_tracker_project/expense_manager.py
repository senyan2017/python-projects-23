import math


def parse_amount(raw):
    """Parse and validate an expense amount.

    Accepts a string or a number and returns a positive float rounded to two
    decimals. Raises ValueError with a clear message on invalid input.
    """
    # bool is a subclass of int; reject it so True/False aren't treated as 1/0.
    if isinstance(raw, bool):
        raise ValueError("Amount must be a valid number (e.g., 12.50).")
    try:
        amount = float(raw)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number (e.g., 12.50).")
    if not math.isfinite(amount):
        raise ValueError("Amount must be a finite number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return round(amount, 2)


class ExpenseManager:
    def __init__(self):
        self.expenses = []

    def add_expense(self, amount, category, description):
        """Add a new expense with amount, category, and description.

        The amount is validated/normalized via ``parse_amount``. An empty
        category or description falls back to a sensible default. Raises
        ValueError if the amount is invalid.
        """
        amount = parse_amount(amount)
        category = (category or "").strip() or "Uncategorized"
        description = (description or "").strip() or "No description"
        expense = {"amount": amount, "category": category, "description": description}
        self.expenses.append(expense)
        return expense

    def list_expenses(self):
        """Return the list of all expenses."""
        return self.expenses

    def get_summary(self):
        """Return a summary of expenses by category, skipping malformed records."""
        summary = {}
        for expense in self.expenses:
            if not isinstance(expense, dict):
                continue
            category = expense.get("category") or "Uncategorized"
            try:
                amount = float(expense.get("amount"))
            except (TypeError, ValueError):
                continue
            if not math.isfinite(amount):
                continue
            summary[category] = summary.get(category, 0) + amount
        return summary
