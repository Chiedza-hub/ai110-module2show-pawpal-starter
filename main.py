from datetime import datetime
from pawpal_system import Owner, Pet, CareTask

# Create owner
owner = Owner(name="Jordan", email="jordan@email.com", phone="555-1234")

# Create two pets
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)

owner.add_pet(mochi)
owner.add_pet(luna)

# Add tasks for Mochi
mochi.schedule.add_task(CareTask(
    title="Morning walk",
    category="exercise",
    priority="high",
    due_date=datetime.today().replace(hour=8, minute=0, second=0, microsecond=0),
))

mochi.schedule.add_task(CareTask(
    title="Feed breakfast",
    category="feeding",
    priority="high",
    due_date=datetime.today().replace(hour=7, minute=30, second=0, microsecond=0),
))

# Add task for Luna
luna.schedule.add_task(CareTask(
    title="Clean litter box",
    category="grooming",
    priority="medium",
    due_date=datetime.today().replace(hour=9, minute=0, second=0, microsecond=0),
))

luna.schedule.add_task(CareTask(
    title="Administer flea medication",
    category="medical",
    priority="high",
    due_date=datetime.today().replace(hour=10, minute=0, second=0, microsecond=0),
))

# Print today's schedule
print(f"=== Today's Schedule for {owner.name} ===\n")

todays_tasks = owner.get_todays_schedule()

if not todays_tasks:
    print("No tasks scheduled for today.")
else:
    sorted_tasks = sorted(todays_tasks, key=lambda t: t.due_date)
    for task in sorted_tasks:
        pet_name = task.assigned_pet.name if task.assigned_pet else "Unknown"
        time_str = task.due_date.strftime("%I:%M %p")
        status = "✓" if task.is_completed else "○"
        print(f"  {status} [{time_str}] {task.title} — {pet_name} ({task.priority} priority)")
