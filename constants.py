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
}

SORT_OPTIONS = ["created", "priority", "alpha"]

DATA_FILE = Path.home() / ".taskmaster_ai.json"

COLOR_PAIRS = {
    "header_title": (1, "white", "blue"),
    "header_time": (2, "black", "white"),
    "header_filter": (3, "yellow", "black"),
    "footer": (4, "black", "cyan"),
    "empty_message": (5, "cyan", "black"),
    "task_done": (6, "green", "black"),
    "task_done_selected": (7, "black", "green"),
    "task_pending_selected": (8, "black", "white"),
    "task_priority_high": (9, "red", "black"),
    "task_priority_medium": (10, "yellow", "black"),
    "task_priority_low": (11, "blue", "black"),
    "scroll_indicator": (12, "magenta", "black"),
    "search_highlight": (13, "black", "yellow"),
}

MAX_DESCRIPTION_LENGTH = 200
MAX_VISIBLE_TASKS = 100
