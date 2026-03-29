from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
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
        pass

    def is_due_today(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


@dataclass
class Schedule:
    pet: Pet = None
    tasks: list = field(default_factory=list)
    reminders_enabled: bool = True

    def add_task(self, task: CareTask):
        pass

    def remove_task(self, task_id: str):
        pass

    def get_upcoming_tasks(self, days: int = 7) -> list:
        pass

    def get_overdue_tasks(self) -> list:
        pass

    def complete_task(self, task_id: str):
        pass


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
        if self.schedule is None:
            self.schedule = Schedule(pet=self)

    def get_active_tasks(self) -> list:
        pass

    def get_task_history(self) -> list:
        pass

    def add_medication(self, med: str):
        pass

    def remove_medication(self, med: str):
        pass


@dataclass
class Owner:
    name: str
    email: str = ""
    phone: str = ""
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        pass

    def remove_pet(self, pet_id: str):
        pass

    def get_all_pets(self) -> list:
        pass

    def get_all_tasks(self) -> list:
        return [task for pet in self.pets for task in pet.schedule.tasks]

    def get_todays_schedule(self) -> list:
        today = datetime.today().date()
        return [t for t in self.get_all_tasks() if t.due_date.date() == today]

    def get_tasks_for_pet(self, pet_id: str) -> list:
        pass

    def get_pet_schedule(self, pet_id: str) -> Schedule:
        pass
