# TaskMaster AI - Professional TUI Task Manager

A full-screen, modern terminal task manager built with Python curses. Features a clean interface with keyboard navigation, priority management, search, and sorting capabilities.

## Features

- **Modern Dashboard** - Full-screen UI with border, header stats, and footer controls
- **Priority System** - Low (blue), Medium (yellow), High (red) priority levels
- **Search & Sort** - Full-text search and multiple sort options
- **Smart Filtering** - Filter by All/Pending/Done status
- **Visual Feedback** - Color-coded tasks, full-width selection bar, notifications
- **Keyboard Navigation** - Full keyboard control with Home/End support
- **Persistent Storage** - Auto-saves to `~/.taskmaster_ai.json`

## Controls

| Key | Action |
|-----|--------|
| `n` | Add new task |
| `d` | Delete task (with confirmation) |
| `e` | Edit task description |
| `p` | Change priority |
| `Space` | Toggle task status |
| `s` | Search tasks |
| `r` | Cycle sort (created/priority/alpha) |
| `R` | Toggle sort order |
| `↑/↓` or `j/k` | Navigate tasks |
| `Home` | Jump to first task |
| `End` | Jump to last task |
| `Tab` | Cycle filters (All → Pending → Done) |
| `q` | Quit |

## Installation

### Quick Start

```bash
# Run directly
python3 -m taskmaster

# Or make executable and run
chmod +x taskmaster.py
./taskmaster.py
```

### Global Install

```bash
# Install via pip for global access
pip install --user .

# Then run from anywhere
taskmaster
```

### Create Alias

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias t='python3 /path/to/taskmaster.py'
```

## Requirements

- Python 3.7+
- curses library (included with Python on Linux/macOS)
- No external dependencies

## Data Storage

Tasks are saved to `~/.taskmaster_ai.json`:

```json
[
  {
    "id": "uuid",
    "description": "Task description",
    "status": "PENDING|DONE",
    "priority": "LOW|MEDIUM|HIGH",
    "created_at": "ISO timestamp",
    "due_date": null,
    "updated_at": "ISO timestamp"
  }
]
```

## License

MIT
