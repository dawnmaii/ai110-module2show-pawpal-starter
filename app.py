import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize all session_state keys before any code reads them.
# Streamlit reruns the entire script on every interaction, so these guards prevent KeyError on first load.
if "owners" not in st.session_state:
    st.session_state.owners = {}  # dict mapping owner name → Owner object; persists across reruns
if "current_owner_name" not in st.session_state:
    st.session_state.current_owner_name = None
if "last_owner_name" not in st.session_state:
    st.session_state.last_owner_name = None  # used to detect when the user switches owners
if "owner_input_key" not in st.session_state:
    st.session_state.owner_input_key = 0  # incrementing this key forces Streamlit to recreate the widget, clearing the input
if "pet_input_key" not in st.session_state:
    st.session_state.pet_input_key = 0  # same counter pattern for the pet name/species inputs
if "task_input_key" not in st.session_state:
    st.session_state.task_input_key = 0  # same counter pattern for all task input fields
if "pet_include" not in st.session_state:
    st.session_state.pet_include = {}  # dict keyed by (owner_name, pet_name); stores per-pet checkbox state across reruns
if "last_plan" not in st.session_state:
    st.session_state.last_plan = []  # most recently generated schedule; displayed below the generate button
if "task_to_pet" not in st.session_state:
    st.session_state.task_to_pet = {}  # maps id(task) → pet name; id() used because tasks may have identical field values
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "both (priority, then duration)"
if "filter_priority" not in st.session_state:
    st.session_state.filter_priority = None  # None = not yet set (show all); [] = deliberately cleared (show nothing)
if "filter_pet" not in st.session_state:
    st.session_state.filter_pet = None

st.markdown("""
<style>
/* Neutralize the default red/primary-color pill background on all multiselect tags
   so the emoji prefix becomes the sole color indicator. */
span[data-baseweb="tag"] {
    background-color: #e8f0f7 !important;
    border: 1px solid #b3cde0 !important;
}
span[data-baseweb="tag"] span {
    color: #1a1a2e !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🐾 PawPal+")

st.divider()

# --- Owner selector ---
st.subheader("Owner")

new_owner_name = st.text_input("Add new owner", value="", key=f"new_owner_{st.session_state.owner_input_key}")
if st.button("Add owner"):
    new_owner_name = new_owner_name.strip()  # reject whitespace-only input
    if new_owner_name and new_owner_name not in st.session_state.owners:
        st.session_state.owners[new_owner_name] = Owner(name=new_owner_name)
        st.session_state.current_owner_name = new_owner_name
        st.session_state.owner_input_key += 1  # clear the input field on next render
        st.rerun()
    elif new_owner_name in st.session_state.owners:
        st.warning(f"'{new_owner_name}' already exists.")
    else:
        st.warning("Please enter an owner name.")

if st.session_state.owners:
    selected = st.selectbox(
        "Switch owner",
        options=list(st.session_state.owners.keys()),
        # guard: if current_owner_name is stale (e.g. after page reload), fall back to index 0
        index=list(st.session_state.owners.keys()).index(st.session_state.current_owner_name)
        if st.session_state.current_owner_name in st.session_state.owners else 0,
    )
    st.session_state.current_owner_name = selected
    owner = st.session_state.owners[selected]

    if st.session_state.last_owner_name != selected:
        # Owner switched — clear the stale schedule so the previous owner's plan doesn't show under the new one.
        st.session_state.last_plan = []
        st.session_state.task_to_pet = {}
        st.session_state.last_owner_name = selected
else:
    st.info("Add an owner to get started.")
    st.stop()  # nothing below is renderable without an owner

st.divider()

# --- Add Pet ---
st.subheader("Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="", key=f"pet_name_{st.session_state.pet_input_key}")
with col2:
    species = st.text_input("Species", value="", key=f"species_{st.session_state.pet_input_key}")

if st.button("Add pet"):
    pet_name = pet_name.strip()
    species = species.strip()
    if pet_name and species:
        pet = Pet(name=pet_name, species=species)
        try:
            owner.add_pet(pet)
            st.session_state.pet_input_key += 1  # clear both pet inputs on next render
            st.rerun()
        except ValueError as e:
            st.warning(str(e))
    else:
        st.warning("Please enter both a pet name and species.")

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# --- Add Task ---
st.subheader("Tasks")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Add task to pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="", key=f"task_title_{st.session_state.task_input_key}")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key=f"task_duration_{st.session_state.task_input_key}")
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"], key=f"task_priority_{st.session_state.task_input_key}")

    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"], key=f"task_frequency_{st.session_state.task_input_key}")

    if st.button("Add task"):
        task_title = task_title.strip()
        if not task_title:
            st.warning("Please enter a task title.")
        else:
            priority_map = {"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}
            frequency_map = {"daily": Frequency.DAILY, "weekly": Frequency.WEEKLY, "as needed": Frequency.AS_NEEDED}
            task = Task(
                name=task_title,
                priority=priority_map[priority],
                duration_minutes=int(duration),
                category="general",
                frequency=frequency_map[frequency],
            )
            # selectbox options come directly from owner.pets, so this next() always finds a match
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            try:
                target_pet.add_task(task)
                st.session_state.task_input_key += 1  # clear all task inputs on next render
                st.rerun()
            except ValueError as e:
                st.warning(str(e))

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        show_completed = st.checkbox("Show completed tasks", value=False)
        tasks_to_show = all_tasks if show_completed else [t for t in all_tasks if not t.completed]
        if tasks_to_show:
            st.write("All tasks:")
            st.table([{
                "due date": t.due_date.strftime("%b %d"),
                "task": t.name,
                "priority": t.priority.name.lower(),
                "duration (min)": t.duration_minutes,
                "frequency": "as needed" if t.frequency == Frequency.AS_NEEDED else t.frequency.value,
            } for t in tasks_to_show])
        else:
            st.info("All tasks are completed. Check 'Show completed tasks' to see them.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

# Build checklist from ALL owners (not just current) so pets from multiple owners can be co-scheduled.
checklist_rows = []
for o in st.session_state.owners.values():
    if o.pets:
        for p in o.pets:
            include = st.session_state.pet_include.get((o.name, p.name), True)  # default to included on first render
            checklist_rows.append({"include in schedule": include, "owner": o.name, "pet": p.name, "species": p.species})

if checklist_rows:
    st.write("Select pets to include in the schedule:")
    edited = st.data_editor(
        checklist_rows,
        column_config={"include in schedule": st.column_config.CheckboxColumn("include in schedule")},
        disabled=["owner", "pet", "species"],
        hide_index=True,
        width="stretch",
    )
    # Persist checkbox state so unchecking a pet survives reruns triggered by other widgets.
    for row in edited:
        st.session_state.pet_include[(row["owner"], row["pet"])] = row["include in schedule"]
else:
    edited = []

available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=120)

if st.button("Generate schedule"):
    selected_pets = [r for r in edited if r["include in schedule"]]
    if not selected_pets:
        st.warning("Select at least one pet to schedule.")
    else:
        scheduler = Scheduler(available_minutes=int(available_minutes))
        # First pass: load all selected pets into the scheduler (conflict resolution happens here).
        for row in selected_pets:
            o = st.session_state.owners[row["owner"]]
            pet = next(p for p in o.pets if p.name == row["pet"])
            scheduler.load_tasks_from_pet(pet)

        # Second pass: build task_to_pet AFTER conflict resolution so only surviving tasks are mapped.
        # id(task) is the key because two tasks may have identical field values but be different objects.
        task_to_pet = {}
        for row in selected_pets:
            o = st.session_state.owners[row["owner"]]
            pet = next(p for p in o.pets if p.name == row["pet"])
            for task in pet.tasks:
                if any(t is task for t in scheduler.daily_tasks):  # identity check: was this exact object kept after conflict resolution?
                    task_to_pet[id(task)] = pet.name
        # Parse the human-readable dropdown value back to the sort_key string generate_plan expects.
        sort_key = "both" if "both" in st.session_state.sort_by else ("priority" if "priority" in st.session_state.sort_by else "duration")
        plan = scheduler.generate_plan(sort_by=sort_key)

        if not plan:
            st.warning("No tasks fit in the available time allotted")
            st.session_state.last_plan = []
            st.session_state.task_to_pet = {}
        else:
            st.session_state.last_plan = plan
            st.session_state.task_to_pet = task_to_pet
            # Reset filters so the new plan shows fully on first display.
            st.session_state.filter_priority = None
            st.session_state.filter_pet = None
            st.success(f"Scheduled {len(plan)} task(s) using {scheduler._minutes_used} / {available_minutes} min.")

if st.session_state.last_plan:
    # Re-sort last_plan on every rerun so changing the sort dropdown takes effect without regenerating.
    sort_key = "both" if "both" in st.session_state.sort_by else ("priority" if "priority" in st.session_state.sort_by else "duration")
    if sort_key == "priority":
        sorted_plan = sorted(st.session_state.last_plan, key=lambda t: t.priority.value)
    elif sort_key == "duration":
        sorted_plan = sorted(st.session_state.last_plan, key=lambda t: t.duration_minutes)
    else:
        sorted_plan = sorted(st.session_state.last_plan, key=lambda t: (t.priority.value, t.duration_minutes))

    slot = 8 * 60  # schedule starts at 08:00 (minutes since midnight)
    # Build parallel lists so rows (dicts for display) and tasks (objects) stay in sync after filtering.
    plan_rows = []
    plan_tasks = []
    for task in sorted_plan:
        if task.completed:
            slot += task.duration_minutes  # advance the clock even for completed tasks so subsequent times stay correct
            continue  # AS_NEEDED tasks have no next occurrence so they disappear; recurring ones were already replaced in last_plan
        hours, mins = divmod(slot, 60)
        plan_rows.append({
            "due date": task.due_date.strftime("%b %d"),  # leftmost column so the user can see when each task is due
            "time": f"{hours:02d}:{mins:02d}",
            "task": task.name,
            "pet": st.session_state.task_to_pet.get(id(task), "—"),  # look up pet name by task identity
            "duration (min)": task.duration_minutes,
            "priority": task.priority.name.lower(),
        })
        plan_tasks.append(task)
        slot += task.duration_minutes

    col1, col2, col3 = st.columns(3)
    with col1:
        priority_options = sorted({r["priority"] for r in plan_rows})
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        # `is not None` distinguishes "never set" (show all) from "set to empty list" (show nothing).
        saved_priority = [p for p in (st.session_state.filter_priority if st.session_state.filter_priority is not None else priority_options) if p in priority_options]
        filter_priority = st.multiselect(
            "Filter by priority",
            priority_options,
            default=saved_priority,
            format_func=lambda x: f"{priority_emoji.get(x, '●')} {x}",
        )
        st.session_state.filter_priority = filter_priority  # persist so filter survives reruns
    with col2:
        pet_options = sorted({r["pet"] for r in plan_rows})
        pet_colors = ["🔵", "🟣", "🟠", "🟤", "⚫", "⚪"]
        pet_color_map = {name: pet_colors[i % len(pet_colors)] for i, name in enumerate(pet_options)}
        saved_pet = [p for p in (st.session_state.filter_pet if st.session_state.filter_pet is not None else pet_options) if p in pet_options]
        filter_pet = st.multiselect(
            "Filter by pet",
            pet_options,
            default=saved_pet,
            format_func=lambda x: f"{pet_color_map.get(x, '●')} {x}",
        )
        st.session_state.filter_pet = filter_pet
    with col3:
        st.session_state.sort_by = st.selectbox(
            "Sort by",
            ["both (priority, then duration)", "priority only", "duration only"],
            index=["both (priority, then duration)", "priority only", "duration only"].index(st.session_state.sort_by),
        )

    # Filter both lists together so plan_rows[i] always corresponds to plan_tasks[i].
    paired = [
        (row, task) for row, task in zip(plan_rows, plan_tasks)
        if row["priority"] in filter_priority and row["pet"] in filter_pet
    ]
    filtered = [p[0] for p in paired]
    filtered_tasks = [p[1] for p in paired]

    # Inject current task.completed into each row so the checkbox reflects actual object state on rerender.
    for row, task in zip(filtered, filtered_tasks):
        row["completed"] = task.completed

    edited_schedule = st.data_editor(
        filtered,
        column_config={"completed": st.column_config.CheckboxColumn("completed")},
        disabled=["due date", "time", "task", "pet", "duration (min)", "priority"],
        hide_index=True,
        width="stretch",
    )

    for row, task in zip(edited_schedule, filtered_tasks):
        # `row["completed"] and not task.completed`: only fire on the transition from unchecked → checked.
        # On subsequent reruns the task is already completed, so the condition is False and next_occurrence isn't added again.
        if row["completed"] and not task.completed:
            task.mark_complete()
            next_task = task.next_occurrence()  # returns None for AS_NEEDED tasks
            if next_task:
                # Identity search to find the exact pet object that owns this task, not just any pet with a matching task name.
                pet = next((p for o in st.session_state.owners.values() for p in o.pets if any(t is task for t in p.tasks)), None)
                if pet:
                    try:
                        pet.add_task(next_task)
                        # Replace the completed task with its next occurrence in last_plan so the row
                        # updates in place (new due date, unchecked) instead of disappearing.
                        for i, t in enumerate(st.session_state.last_plan):
                            if t is task:
                                st.session_state.last_plan[i] = next_task
                                break
                        # Carry the pet mapping forward to the new task object.
                        st.session_state.task_to_pet[id(next_task)] = st.session_state.task_to_pet.get(id(task), "—")
                    except ValueError:
                        pass  # next occurrence already exists (e.g. added by a previous run); silently skip
            # AS_NEEDED tasks produce no next_task; the completed task stays in last_plan but is
            # filtered from plan_rows on the next rerun because task.completed is True.
