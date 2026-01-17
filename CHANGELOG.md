# Changelog

## [Unreleased] - 2026-01-17

### Added
- **Due Date Management**: Full UI support for setting and editing task deadlines
  - Press `u` to set/edit due dates
  - Date format: YYYY-MM-DD or YYYY-MM-DD HH:MM
  - Visual indicators for overdue ([OVERDUE]) and due soon ([DUE]) tasks
  - Enter 'none' to clear due dates
- **'e' Key Binding**: Now both `e` and `Enter` can edit task descriptions
- **'m' Key Support**: Archive function now accepts both lowercase `m` and uppercase `M`
- **Comprehensive Test Suite**: Added 200+ lines of tests in tests/ directory
  - test_models.py: Tests for Task model (creation, serialization, deadlines)
  - test_filters.py: Tests for filtering, sorting, and CRUD operations
- **Development Dependencies**: Added pytest, black, isort to pyproject.toml
- **Project Files**:
  - .gitignore with Python and IDE-specific ignores
  - LICENSE file (MIT)
- **Constants**: Moved magic numbers to constants.py
  - MIN_TERMINAL_WIDTH = 60
  - MIN_TERMINAL_HEIGHT = 12

### Fixed
- **Entry Point**: Added main() function to taskmaster.py for proper package installation
- **setup.py README Loading**: Added error handling for missing README.md during installation
- **Consistent Keybindings**: All major keys now accept both upper and lowercase

### Improved
- **Documentation**: Updated README.md with new features and development guidelines
- **Code Quality**: Replaced hardcoded values with named constants
- **Footer**: Updated to show all available shortcuts including new 'u=due'

### Technical Details
- All Python files compile without syntax errors
- Core functionality validated with integration tests
- Task model, filtering, sorting, stats, and archiving all tested and working

## Installation Note
To install with development dependencies:
```bash
pip install -e ".[dev]"
```
