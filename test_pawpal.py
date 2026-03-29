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


# --- Sorting Tests ---

def test_sort_by_time_returns_chronological_order():
    pet = make_pet()
    t1 = CareTask(title="Morning walk", category="exercise", priority="high",
                  due_date=datetime.now() + timedelta(hours=8))
    t2 = CareTask(title="Lunch feeding", category="feeding", priority="medium",
                  due_date=datetime.now() + timedelta(hours=12))
    t3 = CareTask(title="Evening walk", category="exercise", priority="high",
                  due_date=datetime.now() + timedelta(hours=18))

    # Add out of order
    pet.schedule.add_task(t3)
    pet.schedule.add_task(t1)
    pet.schedule.add_task(t2)

    sorted_tasks = pet.schedule.sort_by_time()
    assert [t.title for t in sorted_tasks] == ["Morning walk", "Lunch feeding", "Evening walk"]


def test_sort_by_time_reverse_returns_latest_first():
    pet = make_pet()
    t1 = CareTask(title="Morning walk", category="exercise", priority="high",
                  due_date=datetime.now() + timedelta(hours=8))
    t2 = CareTask(title="Evening walk", category="exercise", priority="high",
                  due_date=datetime.now() + timedelta(hours=18))

    pet.schedule.add_task(t1)
    pet.schedule.add_task(t2)

    sorted_tasks = pet.schedule.sort_by_time(reverse=True)
    assert sorted_tasks[0].title == "Evening walk"
    assert sorted_tasks[1].title == "Morning walk"


def test_sort_by_time_does_not_mutate_original_list():
    pet = make_pet()
    t1 = CareTask(title="First added", category="exercise", priority="low",
                  due_date=datetime.now() + timedelta(hours=18))
    t2 = CareTask(title="Second added", category="feeding", priority="low",
                  due_date=datetime.now() + timedelta(hours=6))

    pet.schedule.add_task(t1)
    pet.schedule.add_task(t2)

    original_order = [t.title for t in pet.schedule.tasks]
    pet.schedule.sort_by_time()

    assert [t.title for t in pet.schedule.tasks] == original_order


def test_sort_empty_schedule_returns_empty_list():
    pet = make_pet()
    assert pet.schedule.sort_by_time() == []


# --- Recurrence Tests ---

def test_completing_daily_task_creates_next_day_task():
    pet = make_pet()
    due = datetime.now()
    task = CareTask(title="Feed breakfast", category="feeding", priority="high",
                    due_date=due, recurrence="daily")
    pet.schedule.add_task(task)

    task_count_before = len(pet.schedule.tasks)
    pet.schedule.complete_task(task.task_id)

    assert task.is_completed is True
    assert len(pet.schedule.tasks) == task_count_before + 1

    new_task = pet.schedule.tasks[-1]
    assert new_task.due_date.date() == (due + timedelta(days=1)).date()


def test_completing_daily_task_inherits_fields():
    pet = make_pet()
    task = CareTask(title="Feed breakfast", category="feeding", priority="high",
                    due_date=datetime.now(), recurrence="daily", notes="Use dry food")
    pet.schedule.add_task(task)
    pet.schedule.complete_task(task.task_id)

    new_task = pet.schedule.tasks[-1]
    assert new_task.title == task.title
    assert new_task.category == task.category
    assert new_task.priority == task.priority
    assert new_task.notes == task.notes
    assert new_task.recurrence == "daily"
    assert new_task.task_id != task.task_id  # fresh ID


def test_completing_non_recurring_task_creates_no_new_task():
    pet = make_pet()
    task = CareTask(title="One-time vet visit", category="medical", priority="high",
                    due_date=datetime.now(), recurrence=None)
    pet.schedule.add_task(task)

    pet.schedule.complete_task(task.task_id)

    assert task.is_completed is True
    assert len(pet.schedule.tasks) == 1  # no new task added


# --- Conflict Detection Tests ---

def test_same_time_tasks_for_same_pet_trigger_conflict():
    pet = make_pet()
    same_time = datetime(2026, 4, 1, 9, 0, 0)
    t1 = CareTask(title="Bath", category="grooming", priority="medium", due_date=same_time)
    t2 = CareTask(title="Feed", category="feeding", priority="high", due_date=same_time)

    pet.schedule.add_task(t1)
    pet.schedule.add_task(t2)

    conflicts = pet.schedule.get_conflicts()
    assert len(conflicts) > 0


def test_different_time_tasks_have_no_conflict():
    pet = make_pet()
    t1 = CareTask(title="Bath", category="grooming", priority="medium",
                  due_date=datetime(2026, 4, 1, 9, 0, 0))
    t2 = CareTask(title="Feed", category="feeding", priority="high",
                  due_date=datetime(2026, 4, 1, 10, 0, 0))

    pet.schedule.add_task(t1)
    pet.schedule.add_task(t2)

    assert pet.schedule.get_conflicts() == []


def test_no_conflicts_on_empty_schedule():
    pet = make_pet()
    assert pet.schedule.get_conflicts() == []
