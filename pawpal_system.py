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
        """Add a task to the schedule and assign it to this pet."""
        task.assigned_pet = self.pet
        self.tasks.append(task)

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
        """Mark a task as completed by its ID, raising ValueError if not found."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.is_completed = True
                return
        raise ValueError(f"No task with id {task_id}")


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
