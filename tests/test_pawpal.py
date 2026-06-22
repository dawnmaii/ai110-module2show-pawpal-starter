from pawpal_system import Pet, Task, Priority


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", priority=Priority.HIGH, duration_minutes=30, category="exercise")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.tasks) == 0
    task = Task(name="Feeding", priority=Priority.HIGH, duration_minutes=10, category="feeding")
    pet.add_task(task)
    assert len(pet.tasks) == 1
