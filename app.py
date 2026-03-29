import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# --- Owner & Pet Setup ---
st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    # Create owner in session state if not already there
    if "owner" not in st.session_state or st.session_state.owner.name != owner_name:
        st.session_state.owner = Owner(name=owner_name)

    owner = st.session_state.owner

    # Check if a pet with this name already exists
    existing_names = owner.get_all_pets()
    if pet_name in existing_names:
        st.warning(f"{pet_name} is already added.")
    else:
        pet = Pet(name=pet_name, species=species, breed="Unknown", age=0)
        owner.add_pet(pet)
        st.success(f"Added {pet_name} to {owner_name}'s pets.")

if "owner" in st.session_state and st.session_state.owner.pets:
    st.write("Pets:", st.session_state.owner.get_all_pets())

st.divider()

# --- Task Scheduling ---
st.subheader("Schedule a Task")
st.caption("Select a pet and add a task to their schedule.")

if "owner" in st.session_state and st.session_state.owner.pets:
    owner = st.session_state.owner
    pet_names = owner.get_all_pets()
    selected_pet_name = st.selectbox("Select pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        category = st.selectbox("Category", ["feeding", "exercise", "grooming", "medical"])
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add Task"):
        # Find the selected pet object
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        task = CareTask(title=task_title, category=category, priority=priority)
        selected_pet.schedule.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}'s schedule.")
else:
    st.info("Add a pet above before scheduling tasks.")

st.divider()

# --- Today's Schedule ---
st.subheader("Today's Schedule")

if st.button("Generate Schedule"):
    if "owner" not in st.session_state or not st.session_state.owner.pets:
        st.warning("Add an owner and at least one pet first.")
    else:
        owner = st.session_state.owner
        todays_tasks = owner.get_todays_schedule()

        if not todays_tasks:
            st.info("No tasks scheduled for today.")
        else:
            sorted_tasks = sorted(todays_tasks, key=lambda t: t.due_date)
            rows = [
                {
                    "Pet": t.assigned_pet.name if t.assigned_pet else "—",
                    "Task": t.title,
                    "Category": t.category,
                    "Priority": t.priority,
                    "Status": "Done" if t.is_completed else "Pending",
                }
                for t in sorted_tasks
            ]
            st.table(rows)
