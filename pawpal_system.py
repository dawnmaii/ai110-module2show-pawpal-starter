from __future__ import annotations  # allows Task | None in Task's own methods without a forward-reference error
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Any  # needed for dict[str, Any] in Owner.preferences


class Priority(Enum):
    # Lower integer value = higher priority; used for numeric comparison in sort and conflict resolution
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Frequency(Enum):
    # String values match what the UI displays and what Frequency.value returns
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as needed"


@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    priority: Priority
    duration_minutes: int
    category: str
    frequency: Frequency = Frequency.DAILY
    completed: bool = False
    due_date: date = field(default_factory=date.today)  # default_factory so each task gets today's date at creation, not a shared default

    def mark_complete(self) -> None:
        self.completed = True

    def next_occurrence(self) -> Task | None:
        # Returns None for AS_NEEDED tasks since there is no fixed recurrence interval.
        if self.frequency == Frequency.DAILY:
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None
        # Copy all fields except completed (new task starts incomplete) and due_date (advanced by frequency).
        return Task(
            name=self.name,
            priority=self.priority,
            duration_minutes=self.duration_minutes,
            category=self.category,
            frequency=self.frequency,
            due_date=next_due,
        )

    def edit_task(self, name: str, priority: Priority, duration_minutes: int, category: str, frequency: Frequency, due_date: date | None = None) -> None:
        # Update all fields in place; due_date is optional so callers can leave it unchanged.
        self.name = name
        self.priority = priority
        self.duration_minutes = duration_minutes
        self.category = category
        self.frequency = frequency
        if due_date is not None:  # only overwrite due_date when explicitly provided
            self.due_date = due_date


@dataclass
class Pet:
    """Stores pet details and a list of associated care tasks."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        # Block duplicates only when an incomplete task with the same name already exists;
        # Completed tasks with the same name are allowed so recurring tasks can coexist with their history.
        if any(t.name == task.name and not t.completed for t in self.tasks):
            raise ValueError(f"Task '{task.name}' already exists for {self.name}.")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        # Identity check (t is task) instead of equality so two tasks with identical field
        # values don't accidentally remove the wrong one.
        for i, t in enumerate(self.tasks):
            if t is task:
                del self.tasks[i]
                return
        raise ValueError(f"Task '{task.name}' not found in {self.name}'s task list.")

    def edit_info(self, name: str, species: str) -> None:
        self.name = name
        self.species = species


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)  # open-ended key-value store for owner settings

    def add_pet(self, pet: Pet) -> None:
        # Prevent duplicate pet names per owner; name is the primary display identifier in the UI.
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"Pet '{pet.name}' already exists for {self.name}.")
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        # Flatten tasks from all pets into a single list; used by the UI's task display table.
        return [task for pet in self.pets for task in pet.tasks]

    def edit_info(self, name: str, preferences: dict[str, Any]) -> None:
        self.name = name
        self.preferences = preferences


@dataclass
class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""
    owner: Owner | None = None  # only required when calling load_tasks_from_owner(); omit when loading pets individually via load_tasks_from_pet()
    available_minutes: int = 480  # default 8-hour day
    daily_tasks: list[Task] = field(default_factory=list)
    _minutes_used: int = field(default=0, init=False, repr=False)  # excluded from __init__ and __repr__; reset each time generate_plan runs
    _loaded_pets: list[Pet] = field(default_factory=list, init=False, repr=False)  # tracks which pets have been loaded to prevent loading the same pet twice

    def load_tasks_from_pet(self, pet: Pet) -> None:
        if any(p is pet for p in self._loaded_pets):  # identity check prevents double-loading if the same object is passed again
            return
        self._loaded_pets.append(pet)
        for task in pet.tasks:
            if task.completed:
                continue  # skip already-completed tasks; they shouldn't appear in today's plan
            # Collect all incomplete tasks already in the pool that share this task's name.
            existing_tasks = [t for t in self.daily_tasks if t.name == task.name and not t.completed]
            if not existing_tasks:
                self.daily_tasks.append(task)
            else:
                best_priority = min(t.priority.value for t in existing_tasks)  # lower value = higher priority
                if task.priority.value < best_priority:
                    # Incoming task has strictly higher priority — displace all existing lower-priority ones.
                    ids_to_remove = {id(t) for t in existing_tasks}  # use id() for identity-based removal; dataclass __eq__ compares fields, not identity
                    self.daily_tasks = [t for t in self.daily_tasks if id(t) not in ids_to_remove]
                    self.daily_tasks.append(task)
                elif task.priority.value == best_priority:
                    self.daily_tasks.append(task)  # tied priority — keep both; different pets may have distinct care needs
                # else: incoming is lower priority than existing — skip it

    def load_tasks_from_owner(self) -> None:
        # Full reload: clear both lists so calling this twice doesn't accumulate duplicates.
        # Requires owner to be set; raises if called without one (use load_tasks_from_pet() instead for multi-owner flows).
        if self.owner is None:
            raise ValueError("load_tasks_from_owner() requires Scheduler.owner to be set.")
        self.daily_tasks = []
        self._loaded_pets = []
        for pet in self.owner.pets:
            self.load_tasks_from_pet(pet)

    def add_task(self, task: Task) -> None:
        # Append a task directly to the pool; call generate_plan() afterwards to refresh _minutes_used.
        self.daily_tasks.append(task)

    def remove_task(self, task: Task) -> None:
        # Identity check so removing one task never accidentally removes another with identical field values.
        for i, t in enumerate(self.daily_tasks):
            if t is task:
                del self.daily_tasks[i]
                return
        raise ValueError(f"Task '{task.name}' not found in the task list.")

    def remaining_minutes(self) -> int:
        return self.available_minutes - self._minutes_used

    def sort_by_priority(self) -> list[Task]:
        # Sort ascending by Priority.value so HIGH (1) comes before MEDIUM (2) before LOW (3).
        return sorted(self.daily_tasks, key=lambda task: task.priority.value)

    def sort_by_duration(self) -> list[Task]:
        # Shortest tasks first; useful for fitting the most tasks into a limited time window.
        return sorted(self.daily_tasks, key=lambda task: task.duration_minutes)

    def generate_plan(self, sort_by: str = "both") -> list[Task]:
        # Reset usage counter so calling generate_plan twice gives independent results.
        self._minutes_used = 0
        if sort_by == "priority":
            plan = [t for t in self.sort_by_priority() if not t.completed]
        elif sort_by == "duration":
            plan = [t for t in self.sort_by_duration() if not t.completed]
        else:
            # "both": priority first, then duration as tiebreaker — most urgent and shortest tasks scheduled first.
            plan = sorted(
                [t for t in self.daily_tasks if not t.completed],
                key=lambda task: (task.priority.value, task.duration_minutes),
            )
        final_plan = []
        for task in plan:
            if task.duration_minutes <= self.remaining_minutes():  # greedy fit: include task only if it fits in remaining time
                final_plan.append(task)
                self._minutes_used += task.duration_minutes
        return final_plan
