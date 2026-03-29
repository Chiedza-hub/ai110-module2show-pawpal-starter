from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CareTask:
    task_id: str
    title: str
    category: str
    priority: str
    due_date: datetime = field(default_factory=datetime.now)
    is_completed: bool = False
    notes: str = ""

    def reschedule(self, new_date: datetime):
        pass

    def is_due_today(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


@dataclass
class Schedule:
    pet_name: str
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
    medications: list = field(default_factory=list)
    schedule: Schedule = None

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

    def remove_pet(self, pet_name: str):
        pass

    def get_all_pets(self) -> list:
        pass

    def get_all_tasks(self) -> list:
        pass

    def get_todays_schedule(self) -> list:
        pass

    def get_tasks_for_pet(self, pet_name: str) -> list:
        pass

    def get_pet_schedule(self, pet_name: str) -> Schedule:
        pass
