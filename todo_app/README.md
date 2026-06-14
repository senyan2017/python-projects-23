# To-Do List Application

## Overview
This is a simple command-line To-Do List application that allows users to:
- View tasks
- Add new tasks
- Mark tasks as completed
- Delete tasks

## Files
- `main.py`: The main script to run the application.
- `todo_list.py`: Contains the `ToDoList` class that manages task operations.
- `tasks.txt`: Stores tasks persistently.

File I/O and the menu loop are shared with the other CLI projects through
the repo-level `common/` package (`common/storage.py`, `common/menu.py`).

## Usage
Run the application by executing:
```bash
python main.py


***Follow the on-screen instructions to manage your tasks.***

```yaml

---

### Step 5: Create `requirements.txt`

Since there are no third-party dependencies in this project, this file can be left empty or omitted.

---

### Running the Project
To run the project, simply execute:

```bash
python main.py

``


## Notes
- **Persistence**: Tasks are saved in tasks.txt, allowing data persistence across program runs.
- **Modularity**: Each component of the application is in a separate file, promoting clean code structure and modularity.
- **Error Handling**: Basic error handling is included for invalid task numbers and menu choices.
