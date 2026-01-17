"""Tests for Task model."""
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from constants import Priority, TaskStatus
from models import Task


class TestTask:
    """Test Task model functionality."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task("Buy groceries")
        assert task.description == "Buy groceries"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM
        assert task.id is not None
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_empty_description(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task("")

    def test_task_creation_with_whitespace_only(self):
        """Test that whitespace-only description raises ValueError."""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task("   ")

    def test_task_description_truncation(self):
        """Test that long descriptions are truncated to 200 chars."""
        long_desc = "a" * 250
        task = Task(long_desc)
        assert len(task.description) == 200

    def test_task_creation_with_priority(self):
        """Test task creation with specific priority."""
        task = Task("Important task", priority=Priority.HIGH)
        assert task.priority == Priority.HIGH

    def test_toggle_status(self):
        """Test toggling task status."""
        task = Task("Test task")
        assert task.status == TaskStatus.PENDING

        task.toggle_status()
        assert task.status == TaskStatus.DONE

        task.toggle_status()
        assert task.status == TaskStatus.PENDING

    def test_update_description(self):
        """Test updating task description."""
        task = Task("Original description")
        task.update_description("Updated description")
        assert task.description == "Updated description"

    def test_update_description_with_empty_string(self):
        """Test that updating with empty description raises ValueError."""
        task = Task("Original")
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            task.update_description("")

    def test_update_priority(self):
        """Test updating task priority."""
        task = Task("Test task")
        assert task.priority == Priority.MEDIUM

        task.update_priority(Priority.HIGH)
        assert task.priority == Priority.HIGH

    def test_set_due_date(self):
        """Test setting due date."""
        task = Task("Test task")
        assert task.due_date is None

        future_date = datetime.now() + timedelta(days=7)
        task.set_due_date(future_date)
        assert task.due_date == future_date

    def test_is_overdue(self):
        """Test overdue detection."""
        task = Task("Test task")
        assert not task.is_overdue()

        # Set past due date
        past_date = datetime.now() - timedelta(days=1)
        task.set_due_date(past_date)
        assert task.is_overdue()

        # Completed tasks are never overdue
        task.toggle_status()
        assert not task.is_overdue()

    def test_is_due_soon(self):
        """Test due soon detection."""
        task = Task("Test task")
        assert not task.is_due_soon()

        # Set due date within 24 hours
        soon_date = datetime.now() + timedelta(hours=12)
        task.set_due_date(soon_date)
        assert task.is_due_soon()

        # Set due date beyond 24 hours
        later_date = datetime.now() + timedelta(days=2)
        task.set_due_date(later_date)
        assert not task.is_due_soon()

    def test_days_until_due(self):
        """Test days until due calculation."""
        task = Task("Test task")
        assert task.days_until_due() is None

        future_date = datetime.now() + timedelta(hours=48)
        task.set_due_date(future_date)
        hours = task.days_until_due()
        assert hours is not None
        assert 47 < hours < 49  # Approximately 48 hours

    def test_get_deadline_status(self):
        """Test deadline status detection."""
        task = Task("Test task")
        assert task.get_deadline_status() == "none"

        # Overdue
        past_date = datetime.now() - timedelta(days=1)
        task.set_due_date(past_date)
        assert task.get_deadline_status() == "overdue"

        # Due soon
        soon_date = datetime.now() + timedelta(hours=12)
        task.set_due_date(soon_date)
        assert task.get_deadline_status() == "soon"

        # Normal (future)
        future_date = datetime.now() + timedelta(days=7)
        task.set_due_date(future_date)
        assert task.get_deadline_status() == "normal"

        # Done (with due date)
        task.toggle_status()
        assert task.get_deadline_status() == "done"

    def test_to_dict(self):
        """Test task serialization to dict."""
        task = Task("Test task", priority=Priority.HIGH)
        task_dict = task.to_dict()

        assert task_dict["description"] == "Test task"
        assert task_dict["status"] == "PENDING"
        assert task_dict["priority"] == "HIGH"
        assert "id" in task_dict
        assert "created_at" in task_dict
        assert "updated_at" in task_dict
        assert task_dict["due_date"] is None

    def test_from_dict(self):
        """Test task deserialization from dict."""
        now = datetime.now()
        task_dict = {
            "id": "test-id-123",
            "description": "Test task",
            "status": "PENDING",
            "priority": "HIGH",
            "created_at": now.isoformat(),
            "due_date": None,
        }

        task = Task.from_dict(task_dict)
        assert task.id == "test-id-123"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.HIGH
        assert task.due_date is None

    def test_from_dict_with_due_date(self):
        """Test task deserialization with due date."""
        now = datetime.now()
        due_date = now + timedelta(days=7)
        task_dict = {
            "id": "test-id-123",
            "description": "Test task",
            "status": "PENDING",
            "priority": "MEDIUM",
            "created_at": now.isoformat(),
            "due_date": due_date.isoformat(),
        }

        task = Task.from_dict(task_dict)
        assert task.due_date is not None
        assert abs((task.due_date - due_date).total_seconds()) < 1

    def test_task_equality(self):
        """Test task equality based on ID."""
        task1 = Task("Task 1", task_id="same-id")
        task2 = Task("Task 2", task_id="same-id")
        task3 = Task("Task 3", task_id="different-id")

        assert task1 == task2
        assert task1 != task3

    def test_task_hash(self):
        """Test task hashing for use in sets/dicts."""
        task1 = Task("Task 1", task_id="id-1")
        task2 = Task("Task 2", task_id="id-2")

        task_set = {task1, task2}
        assert len(task_set) == 2
        assert task1 in task_set
        assert task2 in task_set

    def test_task_repr(self):
        """Test task string representation."""
        task = Task("Test task", priority=Priority.HIGH)
        repr_str = repr(task)
        assert "Test task" in repr_str
        assert "H" in repr_str
        assert "○" in repr_str  # Pending symbol

        task.toggle_status()
        repr_str = repr(task)
        assert "●" in repr_str  # Done symbol

    def test_updated_at_changes(self):
        """Test that updated_at changes on modifications."""
        task = Task("Test task")
        original_updated_at = task.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        task.update_description("New description")
        assert task.updated_at > original_updated_at

    def test_json_serialization_roundtrip(self):
        """Test that task can be serialized and deserialized via JSON."""
        original = Task("Original task", priority=Priority.HIGH)
        original.set_due_date(datetime.now() + timedelta(days=7))

        # Serialize to JSON
        json_str = json.dumps(original.to_dict())

        # Deserialize from JSON
        restored = Task.from_dict(json.loads(json_str))

        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.status == original.status
