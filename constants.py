from enum import Enum, auto
from pathlib import Path


class TaskStatus(Enum):
    PENDING = auto()
    DONE = auto()


class TaskFilter(Enum):
    ALL = auto()
    PENDING = auto()
    DONE = auto()


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


KEYBOARD_SHORTCUTS = {
    "n": "New Task",
    "d": "Delete",
    "e": "Edit",
    "space": "Toggle",
    "up": "↑",
    "down": "↓",
    "tab": "Filter",
    "p": "Priority",
    "s": "Search",
    "q": "Quit",
    "r": "Reverse Sort",
    "shift_d": "Archive Done",
}

SORT_OPTIONS = ["created", "priority", "alpha"]

DATA_FILE = Path.home() / ".taskmaster.json"

MAX_DESCRIPTION_LENGTH = 200
MAX_VISIBLE_TASKS = 100
MIN_TERMINAL_WIDTH = 60
MIN_TERMINAL_HEIGHT = 12

CUSTOM_COLORS = {
    "claude_orange": 20,  # Claude Code signature orange/amber
    "warm_gray": 21,      # Warm gray for text
}

COLOR_PAIRS = {
    "brand_accent": (1, 208, -1),        # Bright orange/amber (Claude orange)
    "text_normal": (2, 252, -1),         # Bright white for main text
    "text_dim": (3, 243, -1),            # Medium gray for secondary text
    "text_bright": (4, 15, -1),          # Pure white for highlights
    "border": (5, 238, -1),              # Subtle gray for borders
    "status_done": (6, 240, -1),         # Dark gray for done items
    "status_pending": (7, 252, -1),      # White for pending
    "priority_high": (8, 196, -1),       # Red for high priority
    "priority_medium": (9, 214, -1),     # Yellow/orange for medium
    "priority_low": (10, 243, -1),       # Gray for low
    "overdue": (11, 196, -1),            # Bright red for overdue
    "due_soon": (12, 214, -1),           # Yellow for due soon
    "progress_bar": (13, 208, -1),       # Claude orange for progress
    "progress_bg": (14, 236, -1),        # Dark gray background
    "search_prompt": (15, 208, -1),      # Orange for search
    "search_bracket": (16, 208, -1),     # Orange brackets
    "header_title": (17, 208, -1),       # Orange title
    "header_time": (18, 243, -1),        # Gray time
    "header_filter_active": (19, 208, -1),   # Orange for active filter
    "header_filter_inactive": (20, 243, -1), # Gray for inactive
    "footer_text": (21, 243, -1),        # Gray footer
    "task_done": (22, 240, -1),          # Dark gray for done tasks
    "task_done_selected": (23, 243, -1), # Medium gray for selected done
}

COLOR_MAP = {
    "brand_blue": 20,
    "white": 7,
    "grey": 8,
    "green": 10,
    "red": 9,
    "yellow": 13,
}

UI_SYMBOLS = {
    "corner_tl": "╭",
    "corner_tr": "╮",
    "corner_bl": "╰",
    "corner_br": "╯",
    "vertical": "│",
    "horizontal": "─",
    "selection": "▸",
    "done": "✔",
    "pending": "○",
    "box_h": "█",
    "box_h_light": "░",
    "box_v": "█",
    "progress_done": "━",
    "progress_pending": "─",
    "bullet": "•",
}

COLUMN_WIDTHS = {
    "status": 3,
    "priority": 4,
    "deadline": 14,
}
