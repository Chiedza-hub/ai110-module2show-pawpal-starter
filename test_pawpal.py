import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, CareTask


# --- Fixtures ---

def make_pet():
    return Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)

def make_task(title="Morning walk", priority="high", days_offset=0):
    return CareTask(
        title=title,
        category="exercise",
        priority=priority,
        due_date=datetime.now() + timedelta(days=days_offset),
    )


# --- Tests ---

def test_task_completion_changes_status():
    pet = make_pet()
    task = make_task()
    pet.schedule.add_task(task)

    assert task.is_completed is False
    pet.schedule.complete_task(task.task_id)
    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.schedule.tasks) == 0

    pet.schedule.add_task(make_task("Feed breakfast"))
    pet.schedule.add_task(make_task("Evening walk"))

    assert len(pet.schedule.tasks) == 2


def test_overdue_tasks_returned_correctly():
    pet = make_pet()
    overdue_task = make_task("Vet visit", days_offset=-2)
    future_task = make_task("Grooming", days_offset=3)

    pet.schedule.add_task(overdue_task)
    pet.schedule.add_task(future_task)

    overdue = pet.schedule.get_overdue_tasks()
    assert len(overdue) == 1
    assert overdue[0].title == "Vet visit"


def test_owner_get_all_pets_returns_names():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3))
    owner.add_pet(Pet(name="Luna", species="cat", breed="Siamese", age=5))

    names = owner.get_all_pets()
    assert names == ["Mochi", "Luna"]


def test_remove_pet_decreases_owner_pet_count():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
    owner.add_pet(pet)

    assert len(owner.pets) == 1
    owner.remove_pet(pet.pet_id)
    assert len(owner.pets) == 0
