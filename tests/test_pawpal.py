import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency


# ── Task.mark_complete ────────────────────────────────────────────────────────

class TestMarkComplete:
    def test_starts_incomplete(self):
        # A newly created task should default to completed=False before mark_complete is ever called.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        assert task.completed is False

    def test_sets_completed_true(self):
        # Calling mark_complete() should flip completed to True.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        assert task.completed is True

    def test_idempotent(self):
        # Calling mark_complete() twice should not raise or reset the flag back to False.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        task.mark_complete()
        assert task.completed is True


# ── Task.next_occurrence ──────────────────────────────────────────────────────

class TestNextOccurrence:
    def test_daily_advances_one_day(self):
        # A DAILY task's next occurrence should be due exactly one day after the original.
        today = date.today()
        task = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY, due_date=today)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == today + timedelta(days=1)

    def test_weekly_advances_seven_days(self):
        # A WEEKLY task's next occurrence should be due exactly seven days after the original.
        today = date.today()
        task = Task("Grooming", Priority.MEDIUM, 15, "grooming", frequency=Frequency.WEEKLY, due_date=today)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == today + timedelta(weeks=1)

    def test_as_needed_returns_none(self):
        # AS_NEEDED tasks have no fixed recurrence interval, so next_occurrence should return None.
        task = Task("Toy", Priority.LOW, 20, "enrichment", frequency=Frequency.AS_NEEDED)
        assert task.next_occurrence() is None

    def test_next_occurrence_starts_incomplete(self):
        # The next occurrence should always start as incomplete regardless of the original task's state.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.completed is False

    def test_next_occurrence_is_new_object(self):
        # next_occurrence must return a brand-new Task object, not a reference to the original.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        nxt = task.next_occurrence()
        assert nxt is not task

    def test_next_occurrence_inherits_all_fields(self):
        # All fields except due_date and completed should be copied from the original to the next occurrence.
        today = date.today()
        task = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY, due_date=today)
        nxt = task.next_occurrence()
        assert nxt.name == task.name
        assert nxt.priority == task.priority
        assert nxt.duration_minutes == task.duration_minutes
        assert nxt.category == task.category
        assert nxt.frequency == task.frequency


# ── Task.edit_task ────────────────────────────────────────────────────────────

class TestEditTask:
    def test_updates_all_fields(self):
        # edit_task should overwrite every field with the provided values.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.edit_task("Run", Priority.MEDIUM, 45, "cardio", Frequency.WEEKLY)
        assert task.name == "Run"
        assert task.priority == Priority.MEDIUM
        assert task.duration_minutes == 45
        assert task.category == "cardio"
        assert task.frequency == Frequency.WEEKLY

    def test_none_due_date_leaves_it_unchanged(self):
        # Passing due_date=None should leave the original due_date untouched.
        original = date.today()
        task = Task("Walk", Priority.HIGH, 30, "exercise", due_date=original)
        task.edit_task("Walk", Priority.HIGH, 30, "exercise", Frequency.DAILY, due_date=None)
        assert task.due_date == original

    def test_explicit_due_date_updates_it(self):
        # Passing an explicit date should overwrite the existing due_date.
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        new_date = date.today() + timedelta(days=5)
        task.edit_task("Walk", Priority.HIGH, 30, "exercise", Frequency.DAILY, due_date=new_date)
        assert task.due_date == new_date


# ── Pet.add_task ──────────────────────────────────────────────────────────────

class TestPetAddTask:
    def test_add_increases_count(self):
        # Adding a task to a pet should increase its task list length by one.
        pet = Pet("Biscuit", "Dog")
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        assert len(pet.tasks) == 1

    def test_add_multiple_distinct_tasks(self):
        # Multiple tasks with different names should all be accepted without error.
        pet = Pet("Biscuit", "Dog")
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        pet.add_task(Task("Feed", Priority.HIGH, 10, "feeding"))
        assert len(pet.tasks) == 2

    def test_duplicate_incomplete_task_raises(self):
        # Adding a task whose name matches an existing incomplete task should raise ValueError.
        pet = Pet("Biscuit", "Dog")
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        with pytest.raises(ValueError, match="Walk"):
            pet.add_task(Task("Walk", Priority.MEDIUM, 20, "exercise"))

    def test_completed_original_allows_same_name(self):
        # Once the original task is marked complete, a new task with the same name (the next occurrence) should be accepted.
        pet = Pet("Biscuit", "Dog")
        original = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY)
        pet.add_task(original)
        original.mark_complete()
        nxt = original.next_occurrence()
        pet.add_task(nxt)  # must not raise
        assert len(pet.tasks) == 2

    def test_adding_to_empty_pet(self):
        # A pet with no tasks should start at count 0 and reach 1 after one add.
        pet = Pet("Biscuit", "Dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        assert len(pet.tasks) == 1


# ── Pet.remove_task ───────────────────────────────────────────────────────────

class TestPetRemoveTask:
    def test_remove_decreases_count(self):
        # Removing the only task on a pet should leave an empty task list.
        pet = Pet("Biscuit", "Dog")
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        pet.add_task(task)
        pet.remove_task(task)
        assert len(pet.tasks) == 0

    def test_remove_nonexistent_raises(self):
        # Trying to remove a task that was never added should raise ValueError.
        pet = Pet("Biscuit", "Dog")
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        with pytest.raises(ValueError, match="Walk"):
            pet.remove_task(task)

    def test_removes_by_identity_not_equality(self):
        # Two tasks with identical field values are different objects.
        # remove_task must remove only the exact object passed, not any equal-looking one.
        pet = Pet("Biscuit", "Dog")
        task_a = Task("Walk", Priority.HIGH, 30, "exercise")
        pet.add_task(task_a)
        task_b = Task("Walk", Priority.HIGH, 30, "exercise")
        task_b.mark_complete()  # distinguish so add_task allows it
        pet.tasks.append(task_b)  # bypass duplicate guard to get two same-named tasks

        pet.remove_task(task_a)

        assert task_a not in pet.tasks
        assert task_b in pet.tasks

    def test_removes_correct_task_among_multiple(self):
        # When a pet has multiple tasks, only the targeted task should be removed.
        pet = Pet("Biscuit", "Dog")
        walk = Task("Walk", Priority.HIGH, 30, "exercise")
        feed = Task("Feed", Priority.HIGH, 10, "feeding")
        pet.add_task(walk)
        pet.add_task(feed)
        pet.remove_task(walk)
        assert walk not in pet.tasks
        assert feed in pet.tasks


# ── Pet.edit_info ─────────────────────────────────────────────────────────────

class TestPetEditInfo:
    def test_updates_name_and_species(self):
        # edit_info should overwrite both name and species in place.
        pet = Pet("Biscuit", "Dog")
        pet.edit_info("Max", "Cat")
        assert pet.name == "Max"
        assert pet.species == "Cat"


# ── Owner.add_pet ─────────────────────────────────────────────────────────────

class TestOwnerAddPet:
    def test_add_increases_count(self):
        # Adding a pet to an owner should increase the pets list length by one.
        owner = Owner("Dawn")
        owner.add_pet(Pet("Biscuit", "Dog"))
        assert len(owner.pets) == 1

    def test_duplicate_name_raises(self):
        # Adding a second pet with the same name should raise ValueError.
        owner = Owner("Dawn")
        owner.add_pet(Pet("Biscuit", "Dog"))
        with pytest.raises(ValueError, match="Biscuit"):
            owner.add_pet(Pet("Biscuit", "Cat"))

    def test_same_name_different_species_still_raises(self):
        # Pet name is the unique key; a different species does not bypass the duplicate check.
        owner = Owner("Dawn")
        owner.add_pet(Pet("Biscuit", "Dog"))
        with pytest.raises(ValueError):
            owner.add_pet(Pet("Biscuit", "Rabbit"))

    def test_add_multiple_distinct_pets(self):
        # Multiple pets with unique names should all be accepted.
        owner = Owner("Dawn")
        owner.add_pet(Pet("Biscuit", "Dog"))
        owner.add_pet(Pet("Esme", "Cat"))
        assert len(owner.pets) == 2


# ── Owner.get_all_tasks ───────────────────────────────────────────────────────

class TestOwnerGetAllTasks:
    def test_no_pets_returns_empty(self):
        # An owner with no pets should return an empty task list.
        owner = Owner("Dawn")
        assert owner.get_all_tasks() == []

    def test_pet_with_no_tasks_returns_empty(self):
        # An owner whose pet has no tasks should still return an empty list.
        owner = Owner("Dawn")
        owner.add_pet(Pet("Biscuit", "Dog"))
        assert owner.get_all_tasks() == []

    def test_flattens_tasks_from_multiple_pets(self):
        # Tasks from all pets should be combined into a single flat list.
        owner = Owner("Dawn")
        dog = Pet("Biscuit", "Dog")
        cat = Pet("Esme", "Cat")
        t1 = Task("Walk", Priority.HIGH, 30, "exercise")
        t2 = Task("Feed", Priority.HIGH, 10, "feeding")
        t3 = Task("Medication", Priority.HIGH, 5, "meds")
        dog.add_task(t1)
        dog.add_task(t2)
        cat.add_task(t3)
        owner.add_pet(dog)
        owner.add_pet(cat)
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 3
        assert t1 in all_tasks and t2 in all_tasks and t3 in all_tasks

    def test_includes_completed_tasks(self):
        # get_all_tasks should return completed tasks too, not filter them out.
        owner = Owner("Dawn")
        pet = Pet("Biscuit", "Dog")
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        pet.tasks.append(task)
        owner.add_pet(pet)
        assert task in owner.get_all_tasks()


# ── Owner.edit_info ───────────────────────────────────────────────────────────

class TestOwnerEditInfo:
    def test_updates_name_and_preferences(self):
        # edit_info should overwrite both name and the preferences dict in place.
        owner = Owner("Dawn", preferences={"style": "structured"})
        owner.edit_info("Alex", {"style": "relaxed"})
        assert owner.name == "Alex"
        assert owner.preferences == {"style": "relaxed"}


# ── Scheduler.load_tasks_from_pet ─────────────────────────────────────────────

class TestLoadTasksFromPet:
    def _setup(self, available_minutes=120):
        owner = Owner("Dawn")
        scheduler = Scheduler(owner=owner, available_minutes=available_minutes)
        return owner, scheduler

    def test_loads_incomplete_tasks(self):
        # Incomplete tasks from a pet should be added to the scheduler's daily_tasks pool.
        owner, scheduler = self._setup()
        pet = Pet("Biscuit", "Dog")
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        owner.add_pet(pet)
        scheduler.load_tasks_from_pet(pet)
        assert len(scheduler.daily_tasks) == 1

    def test_skips_completed_tasks(self):
        # Already-completed tasks should not appear in the scheduler's pool.
        owner, scheduler = self._setup()
        pet = Pet("Biscuit", "Dog")
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        pet.tasks.append(task)
        owner.add_pet(pet)
        scheduler.load_tasks_from_pet(pet)
        assert len(scheduler.daily_tasks) == 0

    def test_identity_guard_prevents_double_load(self):
        # Calling load_tasks_from_pet twice with the same pet object should be a no-op on the second call.
        owner, scheduler = self._setup()
        pet = Pet("Biscuit", "Dog")
        pet.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        owner.add_pet(pet)
        scheduler.load_tasks_from_pet(pet)
        scheduler.load_tasks_from_pet(pet)  # second call is a no-op
        assert len(scheduler.daily_tasks) == 1

    def test_conflict_higher_priority_displaces_lower(self):
        # When two pets have a task with the same name, the higher-priority one should replace the lower.
        owner, scheduler = self._setup()
        pet1 = Pet("Biscuit", "Dog")
        pet2 = Pet("Esme", "Cat")
        low_task = Task("Walk", Priority.LOW, 30, "exercise")
        high_task = Task("Walk", Priority.HIGH, 30, "exercise")
        pet1.add_task(low_task)
        pet2.add_task(high_task)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        scheduler.load_tasks_from_pet(pet1)
        scheduler.load_tasks_from_pet(pet2)
        assert len(scheduler.daily_tasks) == 1
        assert scheduler.daily_tasks[0] is high_task

    def test_conflict_equal_priority_keeps_both(self):
        # When two pets share a task name at the same priority level, both tasks should be kept.
        owner, scheduler = self._setup()
        pet1 = Pet("Biscuit", "Dog")
        pet2 = Pet("Esme", "Cat")
        task1 = Task("Walk", Priority.HIGH, 30, "exercise")
        task2 = Task("Walk", Priority.HIGH, 20, "exercise")
        pet1.add_task(task1)
        pet2.add_task(task2)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        scheduler.load_tasks_from_pet(pet1)
        scheduler.load_tasks_from_pet(pet2)
        assert len(scheduler.daily_tasks) == 2

    def test_conflict_lower_priority_incoming_is_skipped(self):
        # An incoming task with lower priority than the existing one should be silently ignored.
        owner, scheduler = self._setup()
        pet1 = Pet("Biscuit", "Dog")
        pet2 = Pet("Esme", "Cat")
        high_task = Task("Walk", Priority.HIGH, 30, "exercise")
        low_task = Task("Walk", Priority.LOW, 30, "exercise")
        pet1.add_task(high_task)
        pet2.add_task(low_task)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        scheduler.load_tasks_from_pet(pet1)
        scheduler.load_tasks_from_pet(pet2)
        assert len(scheduler.daily_tasks) == 1
        assert scheduler.daily_tasks[0] is high_task

    def test_medium_displaces_low_keeps_high(self):
        # With three pets sharing a task name, MEDIUM should displace LOW but not displace HIGH.
        owner, scheduler = self._setup()
        pet1 = Pet("A", "Dog")
        pet2 = Pet("B", "Cat")
        pet3 = Pet("C", "Bird")
        high = Task("Walk", Priority.HIGH, 30, "exercise")
        low = Task("Walk", Priority.LOW, 30, "exercise")
        med = Task("Walk", Priority.MEDIUM, 30, "exercise")
        pet1.add_task(high)
        pet2.add_task(low)
        pet3.add_task(med)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        owner.add_pet(pet3)
        scheduler.load_tasks_from_pet(pet1)  # HIGH loaded
        scheduler.load_tasks_from_pet(pet2)  # LOW skipped (lower than HIGH)
        scheduler.load_tasks_from_pet(pet3)  # MEDIUM skipped (lower than HIGH)
        assert len(scheduler.daily_tasks) == 1
        assert scheduler.daily_tasks[0] is high


# ── Scheduler.load_tasks_from_owner ──────────────────────────────────────────

class TestLoadTasksFromOwner:
    def test_loads_all_pets(self):
        # load_tasks_from_owner should pull in tasks from every pet the owner has.
        owner = Owner("Dawn")
        dog = Pet("Biscuit", "Dog")
        cat = Pet("Esme", "Cat")
        dog.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        cat.add_task(Task("Medication", Priority.HIGH, 5, "meds"))
        owner.add_pet(dog)
        owner.add_pet(cat)
        scheduler = Scheduler(owner=owner, available_minutes=120)
        scheduler.load_tasks_from_owner()
        assert len(scheduler.daily_tasks) == 2

    def test_reload_does_not_duplicate(self):
        # Calling load_tasks_from_owner a second time should clear and reload, not stack on top of the first load.
        owner = Owner("Dawn")
        dog = Pet("Biscuit", "Dog")
        dog.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        owner.add_pet(dog)
        scheduler = Scheduler(owner=owner, available_minutes=120)
        scheduler.load_tasks_from_owner()
        scheduler.load_tasks_from_owner()  # clears and reloads
        assert len(scheduler.daily_tasks) == 1

    def test_owner_with_no_pets(self):
        # An owner with no pets should result in an empty daily_tasks list after loading.
        owner = Owner("Dawn")
        scheduler = Scheduler(owner=owner, available_minutes=120)
        scheduler.load_tasks_from_owner()
        assert scheduler.daily_tasks == []


# ── Scheduler.remove_task ─────────────────────────────────────────────────────

class TestSchedulerRemoveTask:
    def test_remove_decreases_count(self):
        # Removing the only task in the pool should leave daily_tasks empty.
        owner = Owner("Dawn")
        scheduler = Scheduler(owner=owner, available_minutes=120)
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        scheduler.add_task(task)
        scheduler.remove_task(task)
        assert len(scheduler.daily_tasks) == 0

    def test_remove_nonexistent_raises(self):
        # Attempting to remove a task that was never added should raise ValueError.
        owner = Owner("Dawn")
        scheduler = Scheduler(owner=owner, available_minutes=120)
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        with pytest.raises(ValueError, match="Walk"):
            scheduler.remove_task(task)

    def test_removes_by_identity(self):
        # task_a and task_b have identical fields, so __eq__ can't distinguish them.
        # remove_task must use identity (is) to ensure only the correct object is removed.
        owner = Owner("Dawn")
        scheduler = Scheduler(owner=owner, available_minutes=120)
        task_a = Task("Walk", Priority.HIGH, 30, "exercise")
        task_b = Task("Walk", Priority.HIGH, 30, "exercise")
        scheduler.add_task(task_a)
        scheduler.add_task(task_b)
        scheduler.remove_task(task_a)
        assert not any(t is task_a for t in scheduler.daily_tasks)
        assert any(t is task_b for t in scheduler.daily_tasks)


# ── Scheduler.generate_plan ───────────────────────────────────────────────────

class TestGeneratePlan:
    def _scheduler(self, minutes=120):
        return Scheduler(owner=Owner("Dawn"), available_minutes=minutes)

    def test_empty_pool_returns_empty(self):
        # A scheduler with no tasks should return an empty plan.
        assert self._scheduler().generate_plan() == []

    def test_tasks_that_fit_are_included(self):
        # Tasks whose combined duration fits within available_minutes should all appear in the plan.
        s = self._scheduler(60)
        t1 = Task("Walk", Priority.HIGH, 30, "exercise")
        t2 = Task("Feed", Priority.HIGH, 20, "feeding")
        s.add_task(t1)
        s.add_task(t2)
        plan = s.generate_plan()
        assert t1 in plan and t2 in plan

    def test_task_exceeding_budget_is_excluded(self):
        # A task whose duration alone exceeds available_minutes should not appear in the plan.
        s = self._scheduler(10)
        s.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        assert s.generate_plan() == []

    def test_exactly_fitting_task_is_included(self):
        # A task whose duration exactly equals available_minutes should be included (boundary check).
        s = self._scheduler(30)
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        s.add_task(task)
        assert task in s.generate_plan()

    def test_completed_tasks_excluded(self):
        # Already-completed tasks should be filtered out and not appear in the generated plan.
        s = self._scheduler(120)
        task = Task("Walk", Priority.HIGH, 30, "exercise")
        task.mark_complete()
        s.add_task(task)
        assert s.generate_plan() == []

    def test_minutes_used_tracked(self):
        # After generating a plan, _minutes_used should equal the sum of scheduled task durations.
        s = self._scheduler(120)
        s.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        s.add_task(Task("Feed", Priority.HIGH, 10, "feeding"))
        s.generate_plan()
        assert s._minutes_used == 40

    def test_generate_plan_resets_minutes_used_on_second_call(self):
        # Calling generate_plan a second time should reset _minutes_used and recount from zero.
        s = self._scheduler(120)
        s.add_task(Task("Walk", Priority.HIGH, 30, "exercise"))
        s.generate_plan()
        s.generate_plan()
        assert s._minutes_used == 30

    def test_sort_by_priority_high_first(self):
        # With sort_by="priority", HIGH-priority tasks should appear before LOW-priority ones.
        s = self._scheduler(120)
        low = Task("Low", Priority.LOW, 10, "misc")
        high = Task("High", Priority.HIGH, 10, "misc")
        s.add_task(low)
        s.add_task(high)
        plan = s.generate_plan(sort_by="priority")
        assert plan[0] is high
        assert plan[1] is low

    def test_sort_by_duration_shortest_first(self):
        # With sort_by="duration", the shortest task should be scheduled first.
        s = self._scheduler(120)
        long_task = Task("Long", Priority.HIGH, 60, "misc")
        short_task = Task("Short", Priority.HIGH, 10, "misc")
        s.add_task(long_task)
        s.add_task(short_task)
        plan = s.generate_plan(sort_by="duration")
        assert plan[0] is short_task
        assert plan[1] is long_task

    def test_sort_by_both_priority_then_duration(self):
        # With sort_by="both", tasks are sorted by priority first, then duration as a tiebreaker.
        s = self._scheduler(120)
        high_long = Task("HL", Priority.HIGH, 60, "misc")
        high_short = Task("HS", Priority.HIGH, 10, "misc")
        low_short = Task("LS", Priority.LOW, 5, "misc")
        s.add_task(high_long)
        s.add_task(high_short)
        s.add_task(low_short)
        plan = s.generate_plan(sort_by="both")
        assert plan[0] is high_short  # HIGH priority + shortest duration wins
        assert plan[1] is high_long
        assert plan[2] is low_short

    def test_greedy_skips_oversize_fits_smaller_later(self):
        # The greedy algorithm should skip a task that doesn't fit in the remaining time
        # and continue checking smaller tasks that do fit.
        s = self._scheduler(40)
        t30 = Task("Long", Priority.HIGH, 30, "misc")
        t20 = Task("Med", Priority.MEDIUM, 20, "misc")
        t10 = Task("Short", Priority.LOW, 10, "misc")
        s.add_task(t30)
        s.add_task(t20)
        s.add_task(t10)
        plan = s.generate_plan(sort_by="priority")
        assert t30 in plan      # fits (30 of 40 used)
        assert t20 not in plan  # skipped (20 > 10 remaining)
        assert t10 in plan      # fits in the leftover 10 minutes

    def test_remaining_minutes_after_plan(self):
        # remaining_minutes should reflect the unused time after a plan is generated.
        s = self._scheduler(60)
        s.add_task(Task("Walk", Priority.HIGH, 40, "exercise"))
        s.generate_plan()
        assert s.remaining_minutes() == 20


# ── Scheduler.sort helpers ────────────────────────────────────────────────────

class TestSortHelpers:
    def test_sort_by_priority_all_levels(self):
        # sort_by_priority should return HIGH before MEDIUM before LOW regardless of insertion order.
        owner = Owner("Dawn")
        s = Scheduler(owner=owner, available_minutes=120)
        low = Task("Low", Priority.LOW, 10, "misc")
        med = Task("Med", Priority.MEDIUM, 10, "misc")
        high = Task("High", Priority.HIGH, 10, "misc")
        s.add_task(low)
        s.add_task(med)
        s.add_task(high)
        result = s.sort_by_priority()
        assert result == [high, med, low]

    def test_sort_by_duration_ascending(self):
        # sort_by_duration should return tasks ordered from shortest to longest duration.
        owner = Owner("Dawn")
        s = Scheduler(owner=owner, available_minutes=120)
        s.add_task(Task("A", Priority.HIGH, 60, "misc"))
        s.add_task(Task("B", Priority.HIGH, 10, "misc"))
        s.add_task(Task("C", Priority.HIGH, 30, "misc"))
        result = s.sort_by_duration()
        assert [t.duration_minutes for t in result] == [10, 30, 60]


# ── Recurring task integration ────────────────────────────────────────────────

class TestRecurringTaskFlow:
    def test_completing_and_adding_next_daily(self):
        # Completing a DAILY task and adding its next occurrence should leave exactly one incomplete
        # task on the pet, due the following day.
        pet = Pet("Biscuit", "Dog")
        today = date.today()
        task = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY, due_date=today)
        pet.add_task(task)
        task.mark_complete()
        nxt = task.next_occurrence()
        assert nxt is not None
        pet.add_task(nxt)  # must not raise; original is completed
        incomplete = [t for t in pet.tasks if not t.completed]
        assert len(incomplete) == 1
        assert incomplete[0].due_date == today + timedelta(days=1)

    def test_completing_and_adding_next_weekly(self):
        # Completing a WEEKLY task and adding its next occurrence should schedule it seven days out.
        pet = Pet("Biscuit", "Dog")
        today = date.today()
        task = Task("Grooming", Priority.MEDIUM, 15, "grooming", frequency=Frequency.WEEKLY, due_date=today)
        pet.add_task(task)
        task.mark_complete()
        nxt = task.next_occurrence()
        pet.add_task(nxt)
        assert nxt.due_date == today + timedelta(weeks=1)

    def test_as_needed_produces_no_next_occurrence(self):
        # Completing an AS_NEEDED task should not generate a follow-up task since there's no schedule.
        pet = Pet("Biscuit", "Dog")
        task = Task("Toy", Priority.LOW, 20, "enrichment", frequency=Frequency.AS_NEEDED)
        pet.add_task(task)
        task.mark_complete()
        assert task.next_occurrence() is None

    def test_adding_same_next_occurrence_twice_raises(self):
        # Attempting to add the same next-occurrence task a second time should raise ValueError
        # because a task with that name is already incomplete on the pet.
        pet = Pet("Biscuit", "Dog")
        task = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY)
        pet.add_task(task)
        task.mark_complete()
        nxt = task.next_occurrence()
        pet.add_task(nxt)
        with pytest.raises(ValueError):
            pet.add_task(nxt)  # same name, still incomplete → duplicate

    def test_recurring_task_chain_across_scheduler(self):
        # Full integration: load a task into the scheduler, complete it, add the next occurrence,
        # reload the scheduler, and confirm the new plan contains only the next occurrence.
        owner = Owner("Dawn")
        pet = Pet("Biscuit", "Dog")
        today = date.today()
        task = Task("Walk", Priority.HIGH, 30, "exercise", frequency=Frequency.DAILY, due_date=today)
        pet.add_task(task)
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner, available_minutes=120)
        scheduler.load_tasks_from_owner()
        plan = scheduler.generate_plan()
        assert len(plan) == 1

        task.mark_complete()
        nxt = task.next_occurrence()
        pet.add_task(nxt)

        scheduler.load_tasks_from_owner()  # reload picks up next occurrence, skips completed original
        plan2 = scheduler.generate_plan()
        assert len(plan2) == 1
        assert plan2[0] is nxt
        assert plan2[0].due_date == today + timedelta(days=1)
