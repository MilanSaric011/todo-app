# AGENTS.md - TaskMaster Development Guidelines

This file provides guidelines for coding agents operating in this repository.

## Build, Lint, and Test Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running the Application
```bash
# Run directly
python3 taskmaster.py

# Run as module
python3 -m taskmaster

# After pip install
taskmaster
td  # if alias is set up
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_models.py

# Run a single test function
pytest tests/test_models.py::test_task_creation

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=taskmaster --cov-report=term-missing
```

### Linting and Formatting
```bash
# Format code with Black
black taskmaster.py models.py constants.py

# Check formatting (no changes)
black --check taskmaster.py models.py constants.py

# Sort imports
isort taskmaster.py models.py constants.py

# Run all linters
black --check taskmaster.py models.py constants.py && isort --check-only taskmaster.py models.py constants.py
```

## Code Style Guidelines

### Imports
- Use absolute imports: `from constants import COLOR_PAIRS`
- Group imports: standard library → third-party → local
- Sort imports alphabetically within groups (configured with isort)
- Example:
```python
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from constants import COLOR_PAIRS, DATA_FILE, Priority
from models import Task
```

### Formatting
- Line length: 100 characters (Black default)
- Use trailing commas for multi-line calls
- No blank lines between imports and module docstring
- Two blank lines between top-level definitions
- One blank line between method definitions in a class

### Type Hints
- Use type hints for all function signatures
- Prefer `List[T]`, `Dict[K, V]` from typing (Python 3.7 compatibility)
- Use `Optional[T]` instead of `Union[T, None]`
- Example:
```python
def get_filtered_tasks(self) -> List[Task]:
    ...
def get_user_input(self, prompt: str) -> str:
    ...
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `TaskMaster`, `TaskStatus`)
- **Functions/variables**: snake_case (e.g., `get_filtered_tasks`, `task_list`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `COLOR_PAIRS`, `DATA_FILE`)
- **Private methods**: leading underscore (e.g., `_get_sort_key`)
- **File names**: snake_case (e.g., `taskmaster.py`, `constants.py`)

### Error Handling
- Use try/except blocks with specific exception types
- Always include meaningful error messages
- Log errors with `show_message()` for user feedback
- Example:
```python
try:
    with open(self.data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except (json.JSONDecodeError, IOError, KeyError, ValueError) as e:
    self.tasks = []
    self.show_message(f"Error loading tasks: {e}", timeout=3)
```

### Curses/TUI Specific
- Wrap all `stdscr` operations in try/except blocks
- Use `_safe_addstr()` helper for bounds-checked text output
- Always check terminal size before drawing: `if height < 12 or width < 60: return`
- Use `curses.A_BOLD` for emphasis, `curses.A_DIM` for de-emphasis
- Initialize colors at startup: `curses.start_color()`, `curses.use_default_colors()`
- Use `-1` for transparent background in color pairs

### Docstrings
- Use triple double quotes for docstrings
- One-line docstring for simple functions
- Multi-line docstring with description, args, returns for complex functions
- Example:
```python
def load_tasks(self) -> None:
    """Load tasks from the JSON data file."""
    ...
```

### Commit Messages
Follow conventional commits format:
- `feat: Add new task creation feature`
- `fix: Fix task deletion confirmation dialog`
- `docs: Update README with installation instructions`
- `refactor: Simplify task filtering logic`

### File Organization
- `taskmaster.py` - Main application logic and TUI rendering
- `constants.py` - Configuration, enums, color definitions, UI symbols
- `models.py` - Data models (Task, TaskStatus, Priority)
- `__main__.py` - Entry point for `python3 -m taskmaster`

### Key Configuration
- **Data file**: `~/.taskmaster.json` (JSON format)
- **Default colors**: Zen-Dark inspired theme with #34baeb accent
- **Color pairs**: Defined in `constants.py` with ID, foreground, background
- **UI symbols**: Defined in `UI_SYMBOLS` dictionary for consistency
