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

DATA_FILE = Path.home() / ".taskmaster_ai.json"

MAX_DESCRIPTION_LENGTH = 200
MAX_VISIBLE_TASKS = 100

CUSTOM_COLORS = {
    "brand_blue": 20,
}

COLOR_PAIRS = {
    "brand_accent": (1, 20, -1),
    "text_normal": (2, 7, -1),
    "text_dim": (3, 7, -1),
    "text_bright": (4, 7, -1),
    "border": (5, 8, -1),
    "status_done": (6, 8, -1),
    "status_pending": (7, 7, -1),
    "priority_high": (8, 9, -1),
    "priority_medium": (9, 13, -1),
    "priority_low": (10, 20, -1),
    "overdue": (11, 9, -1),
    "due_soon": (12, 13, -1),
    "progress_bar": (13, 20, -1),
    "progress_bg": (14, 8, -1),
    "search_prompt": (15, 7, -1),
    "search_bracket": (16, 20, -1),
    "header_title": (17, 20, -1),
    "header_time": (18, 8, -1),
    "header_filter_active": (19, 20, -1),
    "header_filter_inactive": (20, 7, -1),
    "footer_text": (21, 7, -1),
    "task_done": (22, 8, -1),
    "task_done_selected": (23, 20, -1),
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
    "selection": "➤",
    "done": "✔",
    "pending": "○",
    "box_h": "█",
    "box_h_light": "░",
    "box_v": "█",
    "progress_done": "✔",
    "progress_pending": "○",
}

COLUMN_WIDTHS = {
    "status": 3,
    "priority": 4,
    "deadline": 14,
}
