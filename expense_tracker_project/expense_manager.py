class ExpenseManager:
    def __init__(self):
        self.expenses = []

    def add_expense(self, amount, category, description):
        """Add a new expense with amount, category, and description.

        Returns True on success, or an error message string on failure.
        """
        # Validate amount
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return "Invalid amount. Please enter a valid number."
        if amount <= 0:
            return "Amount must be a positive number."

        # Validate category
        if not category or not str(category).strip():
            return "Category cannot be empty."
        category = str(category).strip()

        # Validate description (allow empty but warn; treat as optional)
        description = str(description).strip() if description else ""
        if not description:
            description = "(no description)"

        expense = {"amount": amount, "category": category, "description": description}
        self.expenses.append(expense)
        return True

    def list_expenses(self):
        """Return the list of all expenses."""
        return self.expenses

    def get_summary(self):
        """Return a summary of expenses by category.

        Only includes entries with valid numeric amounts.
        """
        summary = {}
        for expense in self.expenses:
            category = expense.get("category", "Uncategorized")
            try:
                amount = float(expense.get("amount", 0))
            except (ValueError, TypeError):
                continue
            summary[category] = summary.get(category, 0.0) + amount
        # Round totals to avoid floating point noise
        return {k: round(v, 2) for k, v in summary.items()}

