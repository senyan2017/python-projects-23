"""A small text-menu loop shared by the CLI projects.

It keeps the common parts in one place (printing the menu, reading the
choice, rejecting bad choices, and not crashing on bad numeric input)
while each project supplies its own labelled actions.
"""


class MenuExit(Exception):
    """Raised by a menu action to stop the menu loop (e.g. an Exit option)."""


def run_menu(title, options):
    """Run a numbered menu until an action raises :class:`MenuExit`.

    ``options`` is a list of ``(label, handler)`` pairs shown in order as
    choices ``1..N``. A handler takes no arguments. Any ``ValueError`` or
    ``IndexError`` raised inside a handler is caught and reported so a bad
    number (or amount) never crashes the program; a handler that wants a
    more specific message can still catch the error itself.
    """
    while True:
        print(f"\n{title}")
        for index, (label, _handler) in enumerate(options, 1):
            print(f"{index}. {label}")

        choice = input("Enter your choice: ")
        if not choice.isdigit() or not (1 <= int(choice) <= len(options)):
            print("Invalid choice. Please try again.")
            continue

        _label, handler = options[int(choice) - 1]
        try:
            handler()
        except MenuExit:
            break
        except (ValueError, IndexError):
            print("Invalid input. Please try again.")
