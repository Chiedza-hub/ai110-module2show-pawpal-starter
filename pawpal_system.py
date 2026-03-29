from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4


@dataclass
class CareTask:
    title: str
    category: str
    priority: str
    assigned_pet: Pet = None
    due_date: datetime = field(default_factory=datetime.now)
    is_completed: bool = False
    notes: str = ""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    recurrence: str = None  # "daily", "weekly", or None

    def reschedule(self, new_date: datetime):
        """Update the task's due date to new_date."""
        self.due_date = new_date

    def is_due_today(self) -> bool:
        """Return True if the task is due today."""
        return self.due_date.date() == datetime.today().date()

    def to_dict(self) -> dict:
        """Serialize the task to a dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "due_date": self.due_date.isoformat(),
            "is_completed": self.is_completed,
            "notes": self.notes,
            "assigned_pet": self.assigned_pet.name if self.assigned_pet else None,
        }


@dataclass
class Schedule:
    pet: Pet = None
    tasks: list = field(default_factory=list)
    reminders_enabled: bool = True

    def add_task(self, task: CareTask):
        """Add a task to the schedule and assign it to this pet.
        Prints a warning if another task is already scheduled at the same time.
        """
        task.assigned_pet = self.pet
        warning = self._check_conflict(task)
        if warning:
            print(f"WARNING: {warning}")
        self.tasks.append(task)

    def _check_conflict(self, new_task: CareTask) -> str:
        """Return a warning string if new_task shares a due_date with an existing task, else empty string."""
        pet_name = self.pet.name if self.pet else "Unknown"
        conflict = next(
            (t for t in self.tasks if t.due_date == new_task.due_date and not t.is_completed),
            None
        )
        if conflict:
            time_str = new_task.due_date.strftime("%b %d %I:%M %p")
            return f"Conflict for {pet_name}: '{new_task.title}' and '{conflict.title}' are both scheduled at {time_str}."
        return ""

    def get_conflicts(self) -> list:
        """Return a list of warning strings for all same-time conflicts in this schedule."""
        pet_name = self.pet.name if self.pet else "Unknown"
        by_time = {}
        for task in self.tasks:
            if not task.is_completed:
                by_time.setdefault(task.due_date, []).append(task)
        warnings = []
        for due_date, group in by_time.items():
            if len(group) > 1:
                time_str = due_date.strftime("%b %d %I:%M %p")
                titles = " and ".join(f"'{t.title}'" for t in group)
                warnings.append(f"Conflict for {pet_name}: {titles} are both scheduled at {time_str}.")
        return warnings

    def remove_task(self, task_id: str):
        """Remove a task from the schedule by its ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_upcoming_tasks(self, days: int = 7) -> list:
        """Return incomplete tasks due within the next N days."""
        cutoff = datetime.today() + timedelta(days=days)
        return [
            t for t in self.tasks
            if not t.is_completed and t.due_date <= cutoff
        ]

    def get_overdue_tasks(self) -> list:
        """Return incomplete tasks whose due date has already passed."""
        now = datetime.now()
        return [
            t for t in self.tasks
            if not t.is_completed and t.due_date < now
        ]

    def complete_task(self, task_id: str):
        """Mark a task as completed by its ID, raising ValueError if not found.
        If the task recurs daily or weekly, a new instance is scheduled automatically.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                task.is_completed = True
                if task.recurrence == "daily":
                    next_due = task.due_date + timedelta(days=1)
                elif task.recurrence == "weekly":
                    next_due = task.due_date + timedelta(weeks=1)
                else:
                    return
                next_task = CareTask(
                    title=task.title,
                    category=task.category,
                    priority=task.priority,
                    due_date=next_due,
                    notes=task.notes,
                    recurrence=task.recurrence,
                )
                self.add_task(next_task)
                return
        raise ValueError(f"No task with id {task_id}")

    def sort_by_time(self, reverse: bool = False) -> list:
        """Return tasks sorted by due_date. Pass reverse=True for latest-first."""
        return sorted(self.tasks, key=lambda t: t.due_date, reverse=reverse)

    def filter_by_status(self, completed: bool) -> list:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.is_completed == completed]

    def filter_by_pet_name(self, name: str) -> list:
        """Return tasks assigned to a pet with the given name (case-insensitive)."""
        return [t for t in self.tasks if t.assigned_pet and t.assigned_pet.name.lower() == name.lower()]


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    pet_id: str = field(default_factory=lambda: str(uuid4()))
    medications: list = field(default_factory=list)
    schedule: Schedule = field(default=None)

    def __post_init__(self):
        """Initialize a Schedule for this pet if one was not provided."""
        if self.schedule is None:
            self.schedule = Schedule(pet=self)

    def get_active_tasks(self) -> list:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.schedule.tasks if not t.is_completed]

    def get_task_history(self) -> list:
        """Return all completed tasks for this pet."""
        return [t for t in self.schedule.tasks if t.is_completed]

    def add_medication(self, med: str):
        """Add a medication to this pet's medication list."""
        self.medications.append(med)

    def remove_medication(self, med: str):
        """Remove a medication from this pet's medication list."""
        self.medications = [m for m in self.medications if m != med]


@dataclass
class Owner:
    name: str
    email: str = ""
    phone: str = ""
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str):
        """Remove a pet from this owner's list by pet ID."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_all_pets(self) -> list:
        """Return the names of all pets owned by this owner."""
        return [p.name for p in self.pets]

    def get_all_tasks(self) -> list:
        """Return all tasks across every pet owned by this owner."""
        return [task for pet in self.pets for task in pet.schedule.tasks]

    def get_todays_schedule(self) -> list:
        """Return all tasks due today across every pet."""
        today = datetime.today().date()
        return [t for t in self.get_all_tasks() if t.due_date.date() == today]

    def get_tasks_for_pet(self, pet_id: str) -> list:
        """Return all tasks for a specific pet by pet ID, raising ValueError if not found."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet.schedule.tasks
        raise ValueError(f"No pet with id {pet_id}")

    def get_pet_schedule(self, pet_id: str) -> Schedule:
        """Return the Schedule for a specific pet by pet ID, raising ValueError if not found."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet.schedule
        raise ValueError(f"No pet with id {pet_id}")

    def get_all_conflicts(self) -> list:
        """Return warning strings for every same-time conflict across all pets."""
        warnings = []
        # Same-pet conflicts
        for pet in self.pets:
            warnings.extend(pet.schedule.get_conflicts())
        # Cross-pet conflicts: tasks from different pets at the same time
        all_tasks = self.get_all_tasks()
        seen = {}
        for task in all_tasks:
            if task.is_completed:
                continue
            key = task.due_date
            pet_name = task.assigned_pet.name if task.assigned_pet else "Unknown"
            if key in seen:
                existing_pet, existing_title = seen[key]
                if existing_pet != pet_name:
                    time_str = task.due_date.strftime("%b %d %I:%M %p")
                    warnings.append(
                        f"Cross-pet conflict at {time_str}: '{existing_title}' ({existing_pet}) "
                        f"and '{task.title}' ({pet_name})."
                    )
            else:
                seen[key] = (pet_name, task.title)
        return warnings
