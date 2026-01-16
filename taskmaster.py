#!/usr/bin/env python3
"""
TaskMaster AI - Professional TUI Task Manager
A full-screen, non-scrolling task manager with keyboard navigation.
"""

import curses
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from constants import COLOR_PAIRS, DATA_FILE, Priority, SORT_OPTIONS, TaskFilter, TaskStatus
from models import Task


EMPTY_STATE_ART = r"""
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║       ╭───────────────────────╮       ║
    ║       │                       │       ║
    ║       │   Nothing to do!      │       ║
    ║       │                       │       ║
    ║       │  Press 'n' to add     │       ║
    ║       │   your first task     │       ║
    ║       │                       │       ║
    ║       ╰───────────────────────╯       ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
"""


class TaskMaster:
    def __init__(self) -> None:
        self.tasks: List[Task] = []
        self.selected_index: int = 0
        self.filter: TaskFilter = TaskFilter.ALL
        self.sort_by: str = "created"
        self.sort_reverse: bool = False
        self.search_query: str = ""
        self.data_file: Path = DATA_FILE
        self.stdscr: Optional[curses._CursesWindow] = None
        self.message: Optional[str] = None
        self.message_timeout: Optional[datetime] = None

    def load_tasks(self) -> None:
        try:
            if self.data_file.exists():
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
        except (json.JSONDecodeError, IOError, KeyError, ValueError) as e:
            self.tasks = []
            self.show_message(f"Error loading tasks: {e}", timeout=3)

    def save_tasks(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.show_message(f"Error saving tasks: {e}", timeout=3)

    def get_filtered_tasks(self) -> List[Task]:
        filtered = self.tasks

        if self.filter == TaskFilter.PENDING:
            filtered = [t for t in filtered if t.status == TaskStatus.PENDING]
        elif self.filter == TaskFilter.DONE:
            filtered = [t for t in filtered if t.status == TaskStatus.DONE]

        if self.search_query:
            query = self.search_query.lower()
            filtered = [t for t in filtered if query in t.description.lower()]

        filtered.sort(key=self._get_sort_key(), reverse=self.sort_reverse)
        return filtered

    def _get_sort_key(self):
        def key(task: Task) -> tuple:
            done_sort = 0 if task.status == TaskStatus.DONE else 1
            if self.sort_by == "priority":
                return (done_sort, task.priority.value, task.created_at)
            elif self.sort_by == "alpha":
                return (done_sort, task.description.lower(), task.created_at)
            else:
                return (done_sort, task.created_at, 0)
        return key

    def show_message(self, message: str, timeout: int = 2) -> None:
        self.message = message
        self.message_timeout = datetime.now()

    def add_task(self, description: str) -> None:
        try:
            task = Task(description)
            self.tasks.insert(0, task)
            self.save_tasks()
            self.selected_index = 0
            self.filter = TaskFilter.ALL
            self.show_message(f"Task added: {task.description[:30]}...")
        except ValueError as e:
            self.show_message(str(e), timeout=3)

    def confirm_delete(self, task: Task) -> bool:
        height, width = self.stdscr.getmaxyx()
        prompt = f'Delete "{task.description[:30]}..." ?'
        prompt_y = height // 2
        prompt_x = max(0, (width - len(prompt)) // 2)
        selected = 0

        while True:
            self.stdscr.clear()
            try:
                self.stdscr.border()
            except curses.error:
                pass
            self._safe_addstr(prompt_y - 2, prompt_x, "DELETE TASK", curses.A_BOLD | curses.color_pair(COLOR_PAIRS["task_priority_high"][0]))
            self._safe_addstr(prompt_y, prompt_x, prompt)

            options = ["YES", "NO"]
            options_y = prompt_y + 2
            for i, opt in enumerate(options):
                marker = "►" if i == selected else "  "
                color = curses.color_pair(COLOR_PAIRS["header_title"][0]) if i == selected else 0
                self._safe_addstr(options_y + i, prompt_x - 2, f"{marker} {opt}", color)

            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key in (curses.KEY_UP, ord("k")) and selected > 0:
                selected -= 1
            elif key in (curses.KEY_DOWN, ord("j")) and selected < len(options) - 1:
                selected += 1
            elif key in (ord("\n"), ord("\r")):
                return selected == 0
            elif key in (ord("q"), ord("Q"), 27):
                return False

        curses.noecho()

    def delete_task(self, index: int) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_delete = filtered_tasks[index]
            if self.confirm_delete(task_to_delete):
                self.tasks.remove(task_to_delete)
                self.save_tasks()
                if self.selected_index >= len(self.get_filtered_tasks()) and self.selected_index > 0:
                    self.selected_index -= 1
                self.show_message(f"Deleted: {task_to_delete.description[:30]}...")

    def toggle_task_status(self, index: int) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task = filtered_tasks[index]
            task.toggle_status()
            self.save_tasks()
            status_text = "completed" if task.status == TaskStatus.DONE else "reopened"
            self.show_message(f"Task {status_text}")

    def edit_task(self, index: int, new_description: str) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task = filtered_tasks[index]
            try:
                task.update_description(new_description)
                self.save_tasks()
                self.show_message("Task updated")
            except ValueError as e:
                self.show_message(str(e), timeout=3)

    def change_priority(self, index: int, priority: Priority) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task = filtered_tasks[index]
            task.update_priority(priority)
            self.save_tasks()
            self.show_message(f"Priority set to {priority.name}")

    def cycle_filter(self) -> None:
        filters = list(TaskFilter)
        current_index = filters.index(self.filter)
        self.filter = filters[(current_index + 1) % len(filters)]
        self.selected_index = 0
        filter_names = {TaskFilter.ALL: "All", TaskFilter.PENDING: "Pending", TaskFilter.DONE: "Done"}
        self.show_message(f"Filter: {filter_names[self.filter]}")

    def cycle_sort(self) -> None:
        current_idx = SORT_OPTIONS.index(self.sort_by)
        self.sort_by = SORT_OPTIONS[(current_idx + 1) % len(SORT_OPTIONS)]
        self.show_message(f"Sort by: {self.sort_by}")

    def toggle_sort_order(self) -> None:
        self.sort_reverse = not self.sort_reverse
        order = "descending" if self.sort_reverse else "ascending"
        self.show_message(f"Sort order: {order}")

    def set_search(self) -> None:
        query = self.get_user_input("Search: ")
        self.search_query = query
        self.selected_index = 0
        if query:
            self.show_message(f'Searching for "{query}"')
        else:
            self.show_message("Search cleared")

    def clear_search(self) -> None:
        self.search_query = ""
        self.show_message("Search cleared")

    def get_current_time(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_stats(self) -> tuple:
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
        done = total - pending
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        return total, pending, done, overdue

    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        if y < 0 or x < 0:
            return
        try:
            height, width = self.stdscr.getmaxyx()
            max_len = width - x - 1
            if max_len <= 0:
                return
            self.stdscr.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    def draw_header(self) -> None:
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return
        if height < 7 or width < 20:
            return

        try:
            self.stdscr.border()
        except curses.error:
            pass

        title = "► TaskMaster AI ◄"
        title_x = max(1, (width - len(title)) // 2)
        self._safe_addstr(0, title_x, title, curses.A_BOLD | curses.color_pair(COLOR_PAIRS["header_title"][0]))

        time_str = self.get_current_time()
        if len(time_str) < width - 4:
            time_x = max(1, width - len(time_str) - 2)
            self._safe_addstr(0, time_x, time_str, curses.color_pair(COLOR_PAIRS["header_time"][0]))

        stats = self.get_stats()
        stats_text = f"Total: {stats[0]} | Pending: {stats[1]} | Done: {stats[2]} | Overdue: {stats[3]}"
        if len(stats_text) < width - 4:
            stats_x = max(1, (width - len(stats_text)) // 2)
            self._safe_addstr(1, stats_x, stats_text, curses.color_pair(COLOR_PAIRS["header_filter"][0]))

        filter_names = {TaskFilter.ALL: "All", TaskFilter.PENDING: "Pending", TaskFilter.DONE: "Done"}
        sort_indicator = "↓" if self.sort_reverse else "↑"
        search_part = '"' + self.search_query + '"' if self.search_query else "Off"
        status_bar = f" Filter: [{filter_names[self.filter]}] | Sort: {self.sort_by[0].upper()}{sort_indicator} | Search: {search_part} "
        if len(status_bar) < width - 4:
            self._safe_addstr(2, 1, status_bar, curses.color_pair(COLOR_PAIRS["footer"][0]))

    def draw_notification(self) -> None:
        if self.message and self.message_timeout:
            elapsed = (datetime.now() - self.message_timeout).total_seconds()
            if elapsed > 2:
                self.message = None
                self.message_timeout = None
                return

        if self.message:
            try:
                height, width = self.stdscr.getmaxyx()
            except curses.error:
                return
            msg_text = f"  ► {self.message}  "
            if len(msg_text) > width - 4:
                msg_text = msg_text[: width - 7] + "...  "
            msg_x = max(1, (width - len(msg_text)) // 2)
            try:
                self.stdscr.addstr(height - 2, msg_x, msg_text, curses.color_pair(COLOR_PAIRS["search_highlight"][0]) | curses.A_BOLD | curses.A_REVERSE)
            except curses.error:
                pass

    def draw_footer(self) -> None:
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return
        if height < 7 or width < 20:
            return

        footer_y = height - 1

        shortcuts = " n=New | d=Del | e=Edit | p=Priority | Space=Toggle | s=Search | r=Sort | ↑↓/jk=Nav | Tab=Filter | Home/End | q=Quit "

        if len(shortcuts) > width - 2:
            shortcuts = shortcuts[: width - 5] + "... "

        try:
            self.stdscr.addstr(footer_y, 0, " " * (width - 1), curses.color_pair(COLOR_PAIRS["footer"][0]) | curses.A_REVERSE)
            self._safe_addstr(footer_y, 1, shortcuts, curses.color_pair(COLOR_PAIRS["footer"][0]) | curses.A_BOLD)
        except curses.error:
            pass

    def draw_tasks(self) -> None:
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return

        if height < 7 or width < 20:
            return

        task_area_height = height - 5
        start_y = 3

        filtered_tasks = self.get_filtered_tasks()

        if not filtered_tasks:
            if self.search_query:
                if self.filter == TaskFilter.DONE:
                    msg = f'No done tasks match "{self.search_query}". Press "Tab" to change filter.'
                elif self.filter == TaskFilter.PENDING:
                    msg = f'No pending tasks match "{self.search_query}". Press "Tab" to change filter.'
                else:
                    msg = f'No tasks match "{self.search_query}". Press "s" to clear search.'
            elif self.filter == TaskFilter.DONE:
                msg = "No done tasks.\n\nPress 'Space' on a task to mark it done.\nPress 'Tab' to see pending tasks."
            elif self.filter == TaskFilter.PENDING:
                msg = "No pending tasks.\n\nAll tasks are done! Great job!\nPress 'Tab' to see all tasks."
            else:
                msg = "No tasks found.\n\nPress 'n' to add a new task."
            
            lines = msg.split('\n')
            start_line = start_y + (task_area_height - len(lines)) // 2
            for i, line in enumerate(lines):
                line_y = start_line + i
                line_x = max(1, (width - len(line)) // 2)
                self._safe_addstr(line_y, line_x, line, curses.color_pair(COLOR_PAIRS["empty_message"][0]) | curses.A_DIM)
            return

        if len(filtered_tasks) > task_area_height:
            start_idx = min(self.selected_index, len(filtered_tasks) - task_area_height)
        else:
            start_idx = 0

        end_idx = min(start_idx + task_area_height, len(filtered_tasks))

        for i in range(start_idx, end_idx):
            task = filtered_tasks[i]
            display_y = start_y + (i - start_idx)

            is_selected = i == self.selected_index

            status_symbol = "✓" if task.status == TaskStatus.DONE else "●"

            priority_colors = {
                Priority.HIGH: curses.color_pair(COLOR_PAIRS["task_priority_high"][0]) | curses.A_BOLD,
                Priority.MEDIUM: curses.color_pair(COLOR_PAIRS["task_priority_medium"][0]),
                Priority.LOW: curses.color_pair(COLOR_PAIRS["task_priority_low"][0]) | curses.A_DIM,
            }

            if task.status == TaskStatus.DONE:
                task_attr = curses.color_pair(COLOR_PAIRS["task_done"][0]) | curses.A_DIM
                priority_attr = curses.color_pair(COLOR_PAIRS["task_done"][0]) | curses.A_DIM
            elif task.is_overdue():
                task_attr = curses.color_pair(COLOR_PAIRS["task_priority_high"][0]) | curses.A_BOLD
                priority_attr = curses.color_pair(COLOR_PAIRS["task_priority_high"][0]) | curses.A_BOLD
            else:
                task_attr = priority_colors[task.priority]
                priority_attr = priority_colors[task.priority]

            line = f" {status_symbol} [{task.priority.name[0]}] {task.description}"

            if task.due_date:
                days = task.days_until_due()
                if days is not None and task.status == TaskStatus.PENDING:
                    if days < 0:
                        line += f" [OVERDUE {-days}d]"
                    elif days == 0:
                        line += " [Due today]"
                    elif days == 1:
                        line += " [Due tomorrow]"
                    elif days <= 7:
                        line += f" [{days}d left]"

            if is_selected:
                try:
                    bg_color = curses.color_pair(COLOR_PAIRS["header_title"][0])
                    self.stdscr.addstr(display_y, 1, " " * (width - 3), bg_color | curses.A_REVERSE)
                except curses.error:
                    pass
                if task.status == TaskStatus.DONE:
                    final_attr = curses.color_pair(COLOR_PAIRS["task_done"][0]) | curses.A_REVERSE
                elif task.is_overdue():
                    final_attr = curses.color_pair(COLOR_PAIRS["task_priority_high"][0]) | curses.A_REVERSE | curses.A_BOLD
                else:
                    final_attr = curses.color_pair(COLOR_PAIRS["task_priority_medium"][0]) | curses.A_REVERSE | curses.A_BOLD
            else:
                final_attr = task_attr

            if len(line) > width - 4:
                line = line[: width - 7] + "... "

            self._safe_addstr(display_y, 2, line, final_attr)

        if len(filtered_tasks) > task_area_height:
            if start_idx > 0:
                self._safe_addstr(start_y - 1, width - 3, "↑", curses.color_pair(COLOR_PAIRS["scroll_indicator"][0]) | curses.A_BOLD)
            if end_idx < len(filtered_tasks):
                self._safe_addstr(start_y + task_area_height, width - 3, "↓", curses.color_pair(COLOR_PAIRS["scroll_indicator"][0]) | curses.A_BOLD)

    def draw_input_prompt(self, prompt: str) -> None:
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return
        prompt_y = max(0, height - 2)

        try:
            self.stdscr.addstr(prompt_y, 0, " " * (width - 1), curses.color_pair(COLOR_PAIRS["search_highlight"][0]))
        except curses.error:
            pass

        if len(prompt) < width - 3:
            try:
                self.stdscr.addstr(prompt_y, 1, prompt + " ", curses.color_pair(COLOR_PAIRS["search_highlight"][0]) | curses.A_BOLD)
                self.stdscr.move(prompt_y, len(prompt) + 2)
            except curses.error:
                pass

        curses.echo()
        self.stdscr.refresh()

    def get_user_input(self, prompt: str) -> str:
        self.draw_input_prompt(prompt)

        input_str = ""
        try:
            input_str = self.stdscr.getstr().decode("utf-8")
        except (KeyboardInterrupt, UnicodeDecodeError):
            input_str = ""

        curses.noecho()
        return input_str.strip()

    def get_priority_selection(self) -> Optional[Priority]:
        options: List[tuple[str, Optional[Priority]]] = [(p.name, p) for p in Priority]
        options.append(("Cancel", None))

        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return None
        menu_y = height // 2 - len(options) // 2
        menu_x = max(0, (width - 20) // 2)

        selected = 0
        while True:
            self.stdscr.clear()
            try:
                self.stdscr.border()
            except curses.error:
                pass
            self._safe_addstr(menu_y - 2, menu_x - 5, "Select Priority:", curses.A_BOLD)

            for i, (name, _) in enumerate(options):
                marker = "►" if i == selected else "  "
                color = curses.color_pair(COLOR_PAIRS["header_title"][0]) if i == selected else 0
                self._safe_addstr(menu_y + i, menu_x - 5, f"{marker} {name}", color)

            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key in (curses.KEY_UP, ord("k")) and selected > 0:
                selected -= 1
            elif key in (curses.KEY_DOWN, ord("j")) and selected < len(options) - 1:
                selected += 1
            elif key in (ord("\n"), ord("\r")):
                return options[selected][1]
            elif key in (ord("q"), ord("Q"), 27):
                return None

        curses.noecho()

    def handle_resize(self) -> None:
        try:
            self.stdscr.clear()
            self.stdscr.refresh()
        except curses.error:
            pass

    def run(self) -> None:
        import os
        if not os.isatty(0):
            print("Error: TaskMaster must be run in an interactive terminal.")
            return

        try:
            self.stdscr = curses.initscr()
        except curses.error as e:
            print(f"Error: Could not initialize terminal - {e}")
            return

        try:
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)
        except curses.error as e:
            curses.endwin()
            print(f"Error: Could not configure terminal - {e}")
            return

        curses.start_color()
        curses.use_default_colors()

        for name, (pair_id, fg, bg) in COLOR_PAIRS.items():
            fg_val = getattr(curses, f"COLOR_{fg.upper()}", curses.COLOR_WHITE)
            bg_val = getattr(curses, f"COLOR_{bg.upper()}", curses.COLOR_BLACK)
            curses.init_pair(pair_id, fg_val, bg_val)

        try:
            self.load_tasks()

            while True:
                try:
                    self.stdscr.clear()
                except curses.error:
                    pass

                filtered_tasks = self.get_filtered_tasks()
                if not filtered_tasks:
                    self.selected_index = 0
                else:
                    self.selected_index = min(self.selected_index, len(filtered_tasks) - 1)

                self.draw_header()
                self.draw_tasks()
                self.draw_notification()
                self.draw_footer()

                try:
                    self.stdscr.refresh()
                except curses.error:
                    pass

                key = self.stdscr.getch()

                if key == curses.KEY_RESIZE:
                    self.handle_resize()
                elif key in (ord("q"), ord("Q")):
                    break
                elif key in (ord("n"), ord("N")):
                    description = self.get_user_input("New task: ")
                    if description:
                        self.add_task(description)
                elif key in (curses.KEY_UP, ord("k")):
                    if self.selected_index > 0:
                        self.selected_index -= 1
                elif key in (curses.KEY_DOWN, ord("j")):
                    filtered_tasks = self.get_filtered_tasks()
                    if self.selected_index < len(filtered_tasks) - 1:
                        self.selected_index += 1
                elif key == curses.KEY_HOME:
                    self.selected_index = 0
                elif key == curses.KEY_END:
                    filtered_tasks = self.get_filtered_tasks()
                    self.selected_index = max(0, len(filtered_tasks) - 1)
                elif key in (ord("d"), ord("D")):
                    self.delete_task(self.selected_index)
                elif key == ord(" "):
                    self.toggle_task_status(self.selected_index)
                elif key in (ord("\n"), ord("\r")):
                    filtered_tasks = self.get_filtered_tasks()
                    if 0 <= self.selected_index < len(filtered_tasks):
                        current_task = filtered_tasks[self.selected_index]
                        new_description = self.get_user_input(f"Edit [{current_task.description[:30]}...]: ")
                        if new_description:
                            self.edit_task(self.selected_index, new_description)
                elif key == ord("\t"):
                    self.cycle_filter()
                elif key in (ord("p"), ord("P")):
                    filtered_tasks = self.get_filtered_tasks()
                    if 0 <= self.selected_index < len(filtered_tasks):
                        priority = self.get_priority_selection()
                        if priority:
                            self.change_priority(self.selected_index, priority)
                elif key in (ord("s"), ord("S")):
                    if self.search_query:
                        self.clear_search()
                    else:
                        self.set_search()
                elif key in (ord("r"), ord("R")):
                    filtered_tasks = self.get_filtered_tasks()
                    if key == ord("R"):
                        self.toggle_sort_order()
                    else:
                        self.cycle_sort()

        finally:
            curses.nocbreak()
            if self.stdscr:
                self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()


if __name__ == "__main__":
    app = TaskMaster()
    app.run()
