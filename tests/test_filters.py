"""Tests for TaskMaster filtering and sorting functionality."""
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from constants import Priority, TaskFilter, TaskStatus
from models import Task
from taskmaster import TaskMaster


class TestFiltering:
    """Test task filtering functionality."""

    def setup_method(self):
        """Set up test TaskMaster instance with temp data file."""
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.app = TaskMaster()
        self.app.data_file = Path(self.temp_file.name)
        
        # Create test tasks
        self.task1 = Task("First task", priority=Priority.HIGH)
        self.task2 = Task("Second task", priority=Priority.MEDIUM)
        self.task3 = Task("Third task", priority=Priority.LOW)
        self.task3.toggle_status()  # Mark as done
        
        self.app.tasks = [self.task1, self.task2, self.task3]

    def teardown_method(self):
        """Clean up temp file."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_filter_all(self):
        """Test filtering for all tasks."""
        self.app.filter = TaskFilter.ALL
        filtered = self.app.get_filtered_tasks()
        assert len(filtered) == 3

    def test_filter_pending(self):
        """Test filtering for pending tasks only."""
        self.app.filter = TaskFilter.PENDING
        filtered = self.app.get_filtered_tasks()
        assert len(filtered) == 2
        assert all(t.status == TaskStatus.PENDING for t in filtered)

    def test_filter_done(self):
        """Test filtering for done tasks only."""
        self.app.filter = TaskFilter.DONE
        filtered = self.app.get_filtered_tasks()
        assert len(filtered) == 1
        assert filtered[0].status == TaskStatus.DONE

    def test_search_query(self):
        """Test search query filtering."""
        self.app.search_query = "first"
        filtered = self.app.get_filtered_tasks()
        assert len(filtered) == 1
        assert "First" in filtered[0].description

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        self.app.search_query = "SECOND"
        filtered = self.app.get_filtered_tasks()
        assert len(filtered) == 1
        assert "Second" in filtered[0].description

    def test_search_with_filter(self):
        """Test combining search and filter."""
        self.app.filter = TaskFilter.PENDING
        self.app.search_query = "task"
        filtered = self.app.get_filtered_tasks()
        # Should find "First task" and "Second task" but not "Third task" (it's done)
        assert len(filtered) == 2
        assert all(t.status == TaskStatus.PENDING for t in filtered)


class TestSorting:
    """Test task sorting functionality."""

    def setup_method(self):
        """Set up test TaskMaster instance."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.app = TaskMaster()
        self.app.data_file = Path(self.temp_file.name)

    def teardown_method(self):
        """Clean up temp file."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_sort_by_created_ascending(self):
        """Test sorting by creation date (oldest first)."""
        now = datetime.now()
        task1 = Task("Third", created_at=now + timedelta(hours=2))
        task2 = Task("First", created_at=now)
        task3 = Task("Second", created_at=now + timedelta(hours=1))
        
        self.app.tasks = [task1, task2, task3]
        self.app.sort_by = "created"
        self.app.sort_reverse = False
        
        filtered = self.app.get_filtered_tasks()
        assert filtered[0].description == "First"
        assert filtered[1].description == "Second"
        assert filtered[2].description == "Third"

    def test_sort_by_created_descending(self):
        """Test sorting by creation date (newest first)."""
        now = datetime.now()
        task1 = Task("First", created_at=now)
        task2 = Task("Second", created_at=now + timedelta(hours=1))
        task3 = Task("Third", created_at=now + timedelta(hours=2))
        
        self.app.tasks = [task1, task2, task3]
        self.app.sort_by = "created"
        self.app.sort_reverse = True
        
        filtered = self.app.get_filtered_tasks()
        assert filtered[0].description == "Third"
        assert filtered[1].description == "Second"
        assert filtered[2].description == "First"

    def test_sort_by_priority(self):
        """Test sorting by priority."""
        task1 = Task("Low priority", priority=Priority.LOW)
        task2 = Task("High priority", priority=Priority.HIGH)
        task3 = Task("Medium priority", priority=Priority.MEDIUM)
        
        self.app.tasks = [task1, task2, task3]
        self.app.sort_by = "priority"
        self.app.sort_reverse = False
        
        filtered = self.app.get_filtered_tasks()
        # Priority.LOW = 1, MEDIUM = 2, HIGH = 3
        assert filtered[0].priority == Priority.LOW
        assert filtered[1].priority == Priority.MEDIUM
        assert filtered[2].priority == Priority.HIGH

    def test_sort_by_alpha(self):
        """Test sorting alphabetically."""
        task1 = Task("Zebra")
        task2 = Task("Apple")
        task3 = Task("Mango")
        
        self.app.tasks = [task1, task2, task3]
        self.app.sort_by = "alpha"
        self.app.sort_reverse = False
        
        filtered = self.app.get_filtered_tasks()
        assert filtered[0].description == "Apple"
        assert filtered[1].description == "Mango"
        assert filtered[2].description == "Zebra"

    def test_done_tasks_sorted_to_bottom(self):
        """Test that done tasks are always sorted to bottom."""
        task1 = Task("A pending")
        task2 = Task("B done")
        task2.toggle_status()
        task3 = Task("C pending")
        
        self.app.tasks = [task1, task2, task3]
        self.app.sort_by = "alpha"
        self.app.sort_reverse = False
        
        filtered = self.app.get_filtered_tasks()
        # Pending tasks should be first
        assert filtered[0].status == TaskStatus.PENDING
        assert filtered[1].status == TaskStatus.PENDING
        # Done task should be last
        assert filtered[2].status == TaskStatus.DONE


class TestTaskOperations:
    """Test task CRUD operations."""

    def setup_method(self):
        """Set up test TaskMaster instance."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.app = TaskMaster()
        self.app.data_file = Path(self.temp_file.name)

    def teardown_method(self):
        """Clean up temp file."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_add_task(self):
        """Test adding a task."""
        assert len(self.app.tasks) == 0
        self.app.add_task("New task")
        assert len(self.app.tasks) == 1
        assert self.app.tasks[0].description == "New task"

    def test_add_task_resets_filter(self):
        """Test that adding a task resets filter to ALL."""
        self.app.filter = TaskFilter.DONE
        self.app.add_task("New task")
        assert self.app.filter == TaskFilter.ALL

    def test_add_task_clears_search(self):
        """Test that adding a task clears search."""
        self.app.search_query = "test"
        self.app.search_active = True
        self.app.add_task("New task")
        assert self.app.search_query == ""
        assert self.app.search_active is False

    def test_toggle_task_status(self):
        """Test toggling task status."""
        task = Task("Test task")
        self.app.tasks = [task]
        
        assert task.status == TaskStatus.PENDING
        self.app.toggle_task_status(0)
        assert self.app.tasks[0].status == TaskStatus.DONE
        
        self.app.toggle_task_status(0)
        assert self.app.tasks[0].status == TaskStatus.PENDING

    def test_edit_task(self):
        """Test editing task description."""
        task = Task("Original")
        self.app.tasks = [task]
        
        self.app.edit_task(0, "Updated")
        assert self.app.tasks[0].description == "Updated"

    def test_change_priority(self):
        """Test changing task priority."""
        task = Task("Test task")
        self.app.tasks = [task]
        
        self.app.change_priority(0, Priority.HIGH)
        assert self.app.tasks[0].priority == Priority.HIGH

    def test_archive_done_tasks(self):
        """Test archiving completed tasks."""
        task1 = Task("Pending")
        task2 = Task("Done 1")
        task2.toggle_status()
        task3 = Task("Done 2")
        task3.toggle_status()
        
        self.app.tasks = [task1, task2, task3]
        assert len(self.app.tasks) == 3
        
        self.app.archive_done_tasks()
        assert len(self.app.tasks) == 1
        assert self.app.tasks[0].description == "Pending"

    def test_archive_with_no_done_tasks(self):
        """Test archiving when no tasks are done."""
        task1 = Task("Pending 1")
        task2 = Task("Pending 2")
        
        self.app.tasks = [task1, task2]
        self.app.archive_done_tasks()
        
        # Nothing should be removed
        assert len(self.app.tasks) == 2


class TestStats:
    """Test statistics functionality."""

    def setup_method(self):
        """Set up test TaskMaster instance."""
        self.app = TaskMaster()

    def test_get_stats_empty(self):
        """Test stats with no tasks."""
        total, pending, done, overdue = self.app.get_stats()
        assert total == 0
        assert pending == 0
        assert done == 0
        assert overdue == 0

    def test_get_stats(self):
        """Test stats calculation."""
        task1 = Task("Pending 1")
        task2 = Task("Pending 2")
        task3 = Task("Done")
        task3.toggle_status()
        
        self.app.tasks = [task1, task2, task3]
        
        total, pending, done, overdue = self.app.get_stats()
        assert total == 3
        assert pending == 2
        assert done == 1
        assert overdue == 0

    def test_get_stats_with_overdue(self):
        """Test stats with overdue tasks."""
        task1 = Task("Overdue")
        task1.set_due_date(datetime.now() - timedelta(days=1))
        task2 = Task("Not overdue")
        
        self.app.tasks = [task1, task2]
        
        total, pending, done, overdue = self.app.get_stats()
        assert total == 2
        assert pending == 2
        assert done == 0
        assert overdue == 1

    def test_get_progress_empty(self):
        """Test progress with no tasks."""
        progress = self.app.get_progress()
        assert progress == 0.0

    def test_get_progress(self):
        """Test progress calculation."""
        task1 = Task("Done 1")
        task1.toggle_status()
        task2 = Task("Done 2")
        task2.toggle_status()
        task3 = Task("Pending")
        task4 = Task("Pending 2")
        
        self.app.tasks = [task1, task2, task3, task4]
        
        progress = self.app.get_progress()
        assert progress == 0.5  # 2 out of 4 done

    def test_cycle_filter(self):
        """Test cycling through filters."""
        self.app.filter = TaskFilter.ALL
        self.app.cycle_filter()
        assert self.app.filter == TaskFilter.PENDING
        
        self.app.cycle_filter()
        assert self.app.filter == TaskFilter.DONE
        
        self.app.cycle_filter()
        assert self.app.filter == TaskFilter.ALL

    def test_cycle_sort(self):
        """Test cycling through sort options."""
        self.app.sort_by = "created"
        self.app.cycle_sort()
        assert self.app.sort_by == "priority"
        
        self.app.cycle_sort()
        assert self.app.sort_by == "alpha"
        
        self.app.cycle_sort()
        assert self.app.sort_by == "created"
