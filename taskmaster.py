#!/usr/bin/env python3
"""
TaskMaster - Professional TUI Task Manager
Claude Code inspired aesthetic with clean, modern design.
"""

import curses
import json
import signal
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from constants import (
    COLOR_PAIRS, COLUMN_WIDTHS, DATA_FILE, 
    MIN_TERMINAL_HEIGHT, MIN_TERMINAL_WIDTH, Priority,
    SORT_OPTIONS, TaskFilter, TaskStatus, UI_SYMBOLS
)
from models import Task


class TaskMaster:
    def __init__(self) -> None:
        self.tasks: List[Task] = []
        self.selected_index: int = 0
        self.filter: TaskFilter = TaskFilter.ALL
        self.sort_by: str = "created"
        self.sort_reverse: bool = False
        self.search_query: str = ""
        self.search_active: bool = False
        self.data_file: Path = DATA_FILE
        self.stdscr: Optional[curses.window] = None
        self.message: Optional[str] = None
        self.message_timeout: Optional[datetime] = None
        self.resize_flag: bool = False

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
            done_sort = 1 if task.status == TaskStatus.DONE else 0
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
            self.search_query = ""
            self.search_active = False
            self.show_message(f"Added: {task.description[:20]}...")
        except ValueError as e:
            self.show_message(str(e), timeout=3)

    def confirm_delete(self, task: Task) -> bool:
        if not self.stdscr: return False
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error:
            return False
            
        prompt = f'Delete "{task.description[:30]}..." ?'
        prompt_y = height // 2
        prompt_x = max(0, (width - len(prompt)) // 2)
        selected = 0

        while True:
            self.stdscr.clear()
            self.stdscr.border()
            self._safe_addstr(prompt_y - 2, prompt_x, " DELETE TASK ", curses.A_BOLD | curses.A_REVERSE | curses.color_pair(COLOR_PAIRS["priority_high"][0]))
            self._safe_addstr(prompt_y, prompt_x, prompt)

            options = ["YES", "NO"]
            for i, opt in enumerate(options):
                marker = UI_SYMBOLS["selection"] if i == selected else " "
                color = curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_BOLD if i == selected else curses.color_pair(COLOR_PAIRS["text_dim"][0])
                self._safe_addstr(prompt_y + 2 + i, prompt_x + 2, f"{marker} {opt}", color)

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

    def delete_task(self, index: int) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_delete = filtered_tasks[index]
            if self.confirm_delete(task_to_delete):
                self.tasks = [t for t in self.tasks if t.id != task_to_delete.id]
                self.save_tasks()
                if self.selected_index >= len(self.get_filtered_tasks()) and self.selected_index > 0:
                    self.selected_index -= 1
                self.show_message("Task deleted")

    def archive_done_tasks(self) -> None:
        done_tasks = [t for t in self.tasks if t.status == TaskStatus.DONE]
        if not done_tasks:
            self.show_message("No done tasks to archive")
            return

        count = len(done_tasks)
        self.tasks = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        self.save_tasks()
        self.selected_index = 0
        self.show_message(f"Archived {count} task(s)")

    def toggle_task_status(self, index: int) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_toggle = filtered_tasks[index]
            for task in self.tasks:
                if task.id == task_to_toggle.id:
                    task.toggle_status()
                    self.save_tasks()
                    status_text = "completed" if task.status == TaskStatus.DONE else "reopened"
                    self.show_message(f"Task {status_text}")
                    return

    def edit_task(self, index: int, new_description: str) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_edit = filtered_tasks[index]
            for task in self.tasks:
                if task.id == task_to_edit.id:
                    try:
                        task.update_description(new_description)
                        self.save_tasks()
                        self.show_message("Task updated")
                    except ValueError as e:
                        self.show_message(str(e), timeout=3)
                    return

    def change_priority(self, index: int, priority: Priority) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_change = filtered_tasks[index]
            for task in self.tasks:
                if task.id == task_to_change.id:
                    task.update_priority(priority)
                    self.save_tasks()
                    self.show_message(f"Priority: {priority.name}")
                    return

    def set_due_date(self, index: int) -> None:
        filtered_tasks = self.get_filtered_tasks()
        if 0 <= index < len(filtered_tasks):
            task_to_update = filtered_tasks[index]
            date_input = self.get_user_input(" Due date (YYYY-MM-DD or 'none'): ")
            if not date_input: return
            
            if date_input.lower() == "none":
                for task in self.tasks:
                    if task.id == task_to_update.id:
                        task.set_due_date(None)
                        self.save_tasks()
                        self.show_message("Due date cleared")
                        return
            try:
                due_date = datetime.strptime(date_input, "%Y-%m-%d")
                due_date = due_date.replace(hour=23, minute=59)
                for task in self.tasks:
                    if task.id == task_to_update.id:
                        task.set_due_date(due_date)
                        self.save_tasks()
                        self.show_message(f"Due: {due_date.strftime('%Y-%m-%d')}")
                        return
            except ValueError:
                self.show_message("Invalid format (use YYYY-MM-DD)")

    def cycle_filter(self) -> None:
        filters = list(TaskFilter)
        current_index = filters.index(self.filter)
        self.filter = filters[(current_index + 1) % len(filters)]
        self.selected_index = 0
        self.show_message(f"Filter: {self.filter.name.lower()}")

    def cycle_sort(self) -> None:
        current_idx = SORT_OPTIONS.index(self.sort_by)
        self.sort_by = SORT_OPTIONS[(current_idx + 1) % len(SORT_OPTIONS)]
        self.show_message(f"Sort: {self.sort_by}")

    def toggle_sort_order(self) -> None:
        self.sort_reverse = not self.sort_reverse
        order = "desc" if self.sort_reverse else "asc"
        self.show_message(f"Order: {order}")

    def set_search(self) -> None:
        self.search_active = True
        self.search_query = ""
        self.selected_index = 0
        self.show_message("Search mode active")

    def clear_search(self) -> None:
        self.search_query = ""
        self.search_active = False
        self.selected_index = 0

    def update_search(self, char: str) -> None:
        if char:
            self.search_query += char
            self.selected_index = 0

    def backspace_search(self) -> None:
        self.search_query = self.search_query[:-1]
        self.selected_index = 0

    def get_current_time(self) -> str:
        return datetime.now().strftime("%H:%M")

    def get_stats(self) -> tuple:
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
        done = total - pending
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        return total, pending, done, overdue

    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        if not self.stdscr: return
        if y < 0 or x < 0: return
        try:
            height, width = self.stdscr.getmaxyx()
            max_len = width - x - 1
            if max_len <= 0: return
            self.stdscr.addstr(y, x, text[:max_len], attr)
        except curses.error: pass

    def draw_header(self) -> None:
        if not self.stdscr: return
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error: return
        
        # Title with reverse colors
        title = " ▸ TaskMaster "
        self._safe_addstr(0, 1, title, curses.A_BOLD | curses.A_REVERSE | curses.color_pair(COLOR_PAIRS["header_title"][0]))

        # Stats - Right Aligned
        stats = self.get_stats()
        stats_text = f"{stats[0]} total · {stats[1]} pending · {stats[2]} done "
        if stats[3] > 0: stats_text += f"· {stats[3]} overdue "
        if len(stats_text) < width - 20:
            self._safe_addstr(0, width - len(stats_text) - 2, stats_text, curses.color_pair(COLOR_PAIRS["text_dim"][0]))

        # Subtitle bar
        filter_names = {TaskFilter.ALL: "all", TaskFilter.PENDING: "pending", TaskFilter.DONE: "done"}
        sort_indicator = "↓" if self.sort_reverse else "↑"
        info = f"view: {filter_names[self.filter]}  ·  sort: {self.sort_by} {sort_indicator}"
        if self.search_query: info += f"  ·  search: {self.search_query}"
        self._safe_addstr(2, 2, info, curses.color_pair(COLOR_PAIRS["text_dim"][0]))

        # Progress
        total = len(self.tasks)
        if total > 0:
            done_count = sum(1 for t in self.tasks if t.status == TaskStatus.DONE)
            pct = done_count / total
            bar_w = min(40, width - 30)
            filled = int(pct * bar_w)
            
            label = " Completion "
            self._safe_addstr(4, 2, label, curses.color_pair(COLOR_PAIRS["brand_accent"][0]))
            
            bar_start = 2 + len(label) + 1
            self._safe_addstr(4, bar_start, UI_SYMBOLS["progress_done"] * filled, curses.color_pair(COLOR_PAIRS["brand_accent"][0]))
            self._safe_addstr(4, bar_start + filled, UI_SYMBOLS["progress_pending"] * (bar_w - filled), curses.color_pair(COLOR_PAIRS["border"][0]))
            self._safe_addstr(4, bar_start + bar_w + 2, f"{int(pct*100)}%", curses.A_BOLD | curses.color_pair(COLOR_PAIRS["brand_accent"][0]))
        
        # Divider
        try:
            self.stdscr.attron(curses.color_pair(COLOR_PAIRS["border"][0]))
            self.stdscr.hline(5, 2, curses.ACS_HLINE, width - 4)
            self.stdscr.attroff(curses.color_pair(COLOR_PAIRS["border"][0]))
        except curses.error: pass

        # Column Headers
        self._safe_addstr(6, 4, "STATUS", curses.A_BOLD | curses.color_pair(COLOR_PAIRS["text_dim"][0]))
        self._safe_addstr(6, 11, "PRIO", curses.A_BOLD | curses.color_pair(COLOR_PAIRS["text_dim"][0]))
        self._safe_addstr(6, 16, "DESCRIPTION", curses.A_BOLD | curses.color_pair(COLOR_PAIRS["text_dim"][0]))

    def draw_tasks(self) -> None:
        if not self.stdscr: return
        try:
            height, width = self.stdscr.getmaxyx()
        except curses.error: return
        
        start_y = 7
        area_h = height - start_y - 3
        filtered = self.get_filtered_tasks()

        if not filtered:
            msg = " No tasks found "
            self._safe_addstr(start_y + 2, (width - len(msg)) // 2, msg, curses.color_pair(COLOR_PAIRS["text_dim"][0]) | curses.A_REVERSE)
            return

        start_idx = 0
        if len(filtered) > area_h:
            start_idx = max(0, min(self.selected_index - area_h // 2, len(filtered) - area_h))

        for i in range(start_idx, min(start_idx + area_h, len(filtered))):
            task = filtered[i]
            y = start_y + (i - start_idx)
            sel = i == self.selected_index
            
            status = UI_SYMBOLS["done"] if task.status == TaskStatus.DONE else UI_SYMBOLS["pending"]
            desc = task.description
            
            # Priority indicator
            prio_sym = "!" * task.priority.value
            prio_color_name = f"priority_{task.priority.name.lower()}"
            prio_c = COLOR_PAIRS[prio_color_name][0] if prio_color_name in COLOR_PAIRS else COLOR_PAIRS["text_dim"][0]
            
            due = ""
            due_c = COLOR_PAIRS["text_dim"][0]
            if task.due_date:
                due = f" {task.due_date.strftime('%b %d')} "
                if task.is_overdue():
                    due = f" OVERDUE {due}"
                    due_c = COLOR_PAIRS["overdue"][0]
                elif task.is_due_soon():
                    due_c = COLOR_PAIRS["due_soon"][0]

            # Adjust max description length to account for column widths
            max_d = width - 20 - len(due)
            if len(desc) > max_d: desc = desc[:max_d-3] + "..."

            if sel:
                self._safe_addstr(y, 1, f" {UI_SYMBOLS['selection']} ", curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_BOLD)
                c_sym = COLOR_PAIRS["brand_accent"][0] if task.status != TaskStatus.DONE else COLOR_PAIRS["task_done"][0]
                self._safe_addstr(y, 6, status, curses.color_pair(c_sym) | curses.A_BOLD)
                
                # Draw priority
                self._safe_addstr(y, 11, prio_sym, curses.color_pair(prio_c) | curses.A_BOLD)
                
                c_txt = COLOR_PAIRS["text_normal"][0] if task.status != TaskStatus.DONE else COLOR_PAIRS["task_done"][0]
                self._safe_addstr(y, 16, desc, curses.color_pair(c_txt) | curses.A_BOLD)
                if due: self._safe_addstr(y, max(16 + len(desc) + 2, width - len(due) - 2), due, curses.color_pair(due_c) | curses.A_BOLD)
            else:
                self._safe_addstr(y, 6, status, curses.color_pair(COLOR_PAIRS["text_dim"][0]))
                
                # Draw priority
                self._safe_addstr(y, 11, prio_sym, curses.color_pair(prio_c))
                
                c_txt = COLOR_PAIRS["text_normal"][0] if task.status != TaskStatus.DONE else COLOR_PAIRS["task_done"][0]
                self._safe_addstr(y, 16, desc, curses.color_pair(c_txt))
                if due: self._safe_addstr(y, max(16 + len(desc) + 2, width - len(due) - 2), due, curses.color_pair(due_c))

    def draw_notification(self) -> None:
        if not self.stdscr or not self.message or not self.message_timeout: return
        if (datetime.now() - self.message_timeout).total_seconds() > 2.5:
            self.message = None
            return
        
        try:
            h, w = self.stdscr.getmaxyx()
            msg = f" {self.message} "
            self._safe_addstr(h - 2, w - len(msg) - 3, msg, curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_REVERSE | curses.A_BOLD)
        except curses.error: pass

    def draw_footer(self) -> None:
        if not self.stdscr: return
        try:
            h, w = self.stdscr.getmaxyx()
        except curses.error: return
        
        keys = [("n", "new"), ("d", "del"), ("e", "edit"), ("space", "toggle"), ("p", "priority"), ("u", "due"), ("s", "search"), ("r", "sort"), ("tab", "filter"), ("m", "archive"), ("q", "quit")]
        x = 2
        for k, a in keys:
            lbl = f" {k} "
            if x + len(lbl) + len(a) + 2 > w: break
            self._safe_addstr(h - 1, x, lbl, curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_REVERSE | curses.A_BOLD)
            x += len(lbl) + 1
            self._safe_addstr(h - 1, x, a, curses.color_pair(COLOR_PAIRS["text_dim"][0]))
            x += len(a) + 2

    def draw_input_prompt(self, prompt: str) -> None:
        if not self.stdscr: return
        try:
            h, w = self.stdscr.getmaxyx()
            self._safe_addstr(h - 2, 2, prompt, curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_BOLD)
            self.stdscr.move(h - 2, 2 + len(prompt))
        except curses.error: pass
        curses.echo()
        self.stdscr.refresh()

    def get_user_input(self, prompt: str) -> str:
        self.draw_input_prompt(prompt)
        try:
            res = self.stdscr.getstr().decode("utf-8")
        except: res = ""
        curses.noecho()
        return res.strip()

    def get_priority_selection(self) -> Optional[Priority]:
        if not self.stdscr: return None
        opts = [(p.name, p) for p in Priority] + [("Cancel", None)]
        sel = 0
        while True:
            self.stdscr.clear()
            self.stdscr.border()
            h, w = self.stdscr.getmaxyx()
            self._safe_addstr(h//2-3, w//2-8, " SELECT PRIORITY ", curses.A_BOLD | curses.A_REVERSE)
            for i, (n, _) in enumerate(opts):
                m = UI_SYMBOLS["selection"] if i == sel else " "
                c = curses.color_pair(COLOR_PAIRS["brand_accent"][0]) | curses.A_BOLD if i == sel else curses.color_pair(COLOR_PAIRS["text_dim"][0])
                self._safe_addstr(h//2-1+i, w//2-5, f"{m} {n}", c)
            self.stdscr.refresh()
            k = self.stdscr.getch()
            if k in (curses.KEY_UP, ord("k")) and sel > 0: sel -= 1
            elif k in (curses.KEY_DOWN, ord("j")) and sel < len(opts)-1: sel += 1
            elif k in (ord("\n"), ord("\r")): return opts[sel][1]
            elif k in (ord("q"), 27): return None

    def handle_resize(self) -> None:
        """Handle terminal resize events."""
        try:
            # Update curses internal representation of screen size
            curses.update_lines_cols()
            if self.stdscr:
                self.stdscr.clear() # Full clear only on resize to remove artifacts
                self.stdscr.refresh()
        except:
            pass

    def run(self) -> None:
        try:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)
            curses.start_color()
            curses.use_default_colors()
            for n, (pid, fg, bg) in COLOR_PAIRS.items():
                try: curses.init_pair(pid, fg, bg if bg >= 0 else -1)
                except: pass
            
            self.load_tasks()
            def handle_winch(sig, frame): self.resize_flag = True
            signal.signal(signal.SIGWINCH, handle_winch)

            while True:
                if self.resize_flag:
                    self.handle_resize()
                    self.resize_flag = False
                
                # Use erase() instead of clear() to prevent flickering
                self.stdscr.erase()
                filtered = self.get_filtered_tasks()
                if filtered: self.selected_index = min(self.selected_index, len(filtered) - 1)
                else: self.selected_index = 0
                
                self.draw_header()
                self.draw_tasks()
                self.draw_notification()
                self.draw_footer()
                self.stdscr.refresh()

                self.stdscr.timeout(100)
                key = self.stdscr.getch()
                if key == -1: continue
                self.stdscr.timeout(-1)

                if key == curses.KEY_RESIZE:
                    self.handle_resize()
                    continue
                elif key in (ord("q"), ord("Q")): break
                
                if self.search_active:
                    if key == 27: self.clear_search()
                    elif key in (curses.KEY_BACKSPACE, 127): self.backspace_search()
                    elif key in (ord("\n"), ord("\r")): self.search_active = False
                    else:
                        try:
                            c = chr(key)
                            if c.isprintable(): self.update_search(c)
                        except: pass
                    continue

                if key in (ord("n"), ord("N")):
                    d = self.get_user_input(" New task: ")
                    if d: self.add_task(d)
                elif key in (curses.KEY_UP, ord("k")):
                    if self.selected_index > 0: self.selected_index -= 1
                elif key in (curses.KEY_DOWN, ord("j")):
                    if self.selected_index < len(filtered) - 1: self.selected_index += 1
                elif key in (ord("d"), ord("D")): self.delete_task(self.selected_index)
                elif key == ord(" "): self.toggle_task_status(self.selected_index)
                elif key in (ord("\n"), ord("\r"), ord("e"), ord("E")):
                    if filtered:
                        curr = filtered[self.selected_index]
                        new_d = self.get_user_input(f" Edit: ")
                        if new_d: self.edit_task(self.selected_index, new_d)
                elif key == ord("\t"): self.cycle_filter()
                elif key in (ord("p"), ord("P")):
                    if filtered:
                        p = self.get_priority_selection()
                        if p: self.change_priority(self.selected_index, p)
                elif key in (ord("s"), ord("S")): self.set_search()
                elif key in (ord("u"), ord("U")):
                    if filtered: self.set_due_date(self.selected_index)
                elif key in (ord("r"), ord("R")):
                    if key == ord("R"): self.toggle_sort_order()
                    else: self.cycle_sort()
                elif key in (ord("m"), ord("M")): self.archive_done_tasks()
        finally:
            curses.nocbreak()
            if self.stdscr: self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

def main() -> None:
    TaskMaster().run()

if __name__ == "__main__":
    main()
