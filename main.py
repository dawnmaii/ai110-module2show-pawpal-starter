from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency

# --- Setup ---
owner = Owner(name="Dawn", preferences={"style": "structured"})

dog = Pet(name="Minh Minh", species="French Bulldog")
cat = Pet(name="Esme", species="Domestic Shorthair")

dog.add_task(Task(name="Morning walk",    priority=Priority.HIGH,   duration_minutes=30,  category="exercise"))
dog.add_task(Task(name="Feeding",         priority=Priority.HIGH,   duration_minutes=10,  category="feeding"))
dog.add_task(Task(name="Enrichment toy",  priority=Priority.LOW,    duration_minutes=20,  category="enrichment", frequency=Frequency.AS_NEEDED))

cat.add_task(Task(name="Medication",      priority=Priority.HIGH,   duration_minutes=5,   category="meds"))
cat.add_task(Task(name="Grooming brush",  priority=Priority.MEDIUM, duration_minutes=15,  category="grooming",   frequency=Frequency.WEEKLY))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Schedule ---
scheduler = Scheduler(owner=owner, available_minutes=120)
scheduler.load_tasks_from_owner()
plan = scheduler.generate_plan()

# --- Output ---
print("=" * 40)
print(f"  Today's Schedule for {owner.name}")
print("=" * 40)

slot = 8 * 60  # start at 08:00
for task in plan:
    hours, mins = divmod(slot, 60)
    print(f"  {hours:02d}:{mins:02d}  {task.name:<20} {task.duration_minutes:>3} min  [{task.priority.name.lower()}]")
    slot += task.duration_minutes

print("-" * 40)
print(f"  Total: {scheduler._minutes_used} / {scheduler.available_minutes} min used")
print("=" * 40)
