class Menu:
    """Simple CLI menu with a title and numbered choices.

    Usage:
        menu = Menu("My App", ["View items", "Add item"])
        choice = menu.get_choice()  # returns "1", "2", or "3" (exit)
    """

    EXIT_LABEL = "Exit"

    def __init__(self, title, choices):
        self.title = title
        self.choices = list(choices)

    def get_choice(self):
        """Display the menu and return the user's valid choice string."""
        print(f"\n{self.title}")
        for i, choice in enumerate(self.choices, 1):
            print(f"{i}. {choice}")
        exit_num = len(self.choices) + 1
        print(f"{exit_num}. {self.EXIT_LABEL}")

        while True:
            raw = input("Enter your choice: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= exit_num:
                return raw
            print("Invalid choice. Please try again.")

    def is_exit(self, choice):
        """Return True if the choice is the exit option."""
        return int(choice) == len(self.choices) + 1

    def run(self, handlers):
        """Run the menu loop. handlers is a list of callables matching choices order."""
        while True:
            choice = self.get_choice()
            if self.is_exit(choice):
                print(f"Exiting {self.title}. Goodbye!")
                break
            idx = int(choice) - 1
            try:
                handlers[idx]()
            except Exception as e:
                print(f"Error: {e}")


def safe_int_input(prompt):
    """Prompt user for an integer, returning None on invalid input."""
    try:
        return int(input(prompt))
    except ValueError:
        return None


def safe_float_input(prompt):
    """Prompt user for a float, returning None on invalid input."""
    try:
        return float(input(prompt))
    except ValueError:
        return None
