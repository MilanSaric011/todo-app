from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from constants import Priority, TaskStatus


class Task:
    __slots__ = ("id", "description", "status", "priority", "created_at", "due_date", "updated_at")

    def __init__(
        self,
        description: str,
        status: TaskStatus = TaskStatus.PENDING,
        priority: Priority = Priority.MEDIUM,
        task_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
    ) -> None:
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")
        if len(description) > 200:
            description = description[:200]

        self.id: str = task_id or str(uuid4())
        self.description: str = description.strip()
        self.status: TaskStatus = status
        self.priority: Priority = priority
        self.created_at: datetime = created_at or datetime.now()
        self.due_date: Optional[datetime] = due_date
        self.updated_at: datetime = self.created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.name,
            "priority": self.priority.name,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            description=data["description"],
            status=TaskStatus[data["status"]],
            priority=Priority[data.get("priority", "MEDIUM")],
            task_id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        )

    def toggle_status(self) -> None:
        self.status = TaskStatus.DONE if self.status == TaskStatus.PENDING else TaskStatus.PENDING
        self.updated_at = datetime.now()

    def update_description(self, new_description: str) -> None:
        if not new_description or not new_description.strip():
            raise ValueError("Task description cannot be empty")
        self.description = new_description.strip()[:200]
        self.updated_at = datetime.now()

    def update_priority(self, priority: Priority) -> None:
        self.priority = priority
        self.updated_at = datetime.now()

    def set_due_date(self, due_date: Optional[datetime]) -> None:
        self.due_date = due_date
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        if self.due_date is None or self.status == TaskStatus.DONE:
            return False
        return datetime.now() > self.due_date

    def is_due_soon(self, hours: int = 24) -> bool:
        if self.due_date is None or self.status == TaskStatus.DONE:
            return False
        return datetime.now() < self.due_date <= datetime.now() + timedelta(hours=hours)

    def days_until_due(self) -> Optional[float]:
        if self.due_date is None:
            return None
        delta = self.due_date - datetime.now()
        return delta.total_seconds() / 3600

    def get_deadline_status(self) -> str:
        if self.due_date is None:
            return "none"
        if self.status == TaskStatus.DONE:
            return "done"
        if self.is_overdue():
            return "overdue"
        if self.is_due_soon():
            return "soon"
        return "normal"

    def __repr__(self) -> str:
        status_symbol = "●" if self.status == TaskStatus.DONE else "○"
        return f"{status_symbol} [{self.priority.name[0]}] {self.description}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
