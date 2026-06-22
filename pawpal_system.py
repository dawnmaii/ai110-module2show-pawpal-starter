from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    priority: Priority
    duration_minutes: int
    category: str
    frequency: Frequency = Frequency.DAILY
    completed: bool = False

    def mark_complete(self) -> None:
        # Mark this task as completed.
        self.completed = True

    def edit_task(self, name: str, priority: Priority, duration_minutes: int, category: str, frequency: Frequency) -> None:
        # Update any of the task's fields in place.
        self.name = name
        self.priority = priority
        self.duration_minutes = duration_minutes
        self.category = category
        self.frequency = frequency


@dataclass
class Pet:
    """Stores pet details and a list of associated care tasks."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        # Append a task to this pet's task list.
        self.tasks.append(task)


    def remove_task(self, task: Task) -> None:
        # Remove a task from this pet's task list; raises ValueError if not found.
        if task in self.tasks:
            self.tasks.remove(task)
        else:
            raise ValueError(f"Task '{task.name}' not found in {self.name}'s task list.")

    def edit_info(self, name: str, species: str) -> None:
        # Update the pet's name and species in place.
        self.name = name
        self.species = species


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        # Append a pet to this owner's pet list.
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        # Remove a pet from this owner's pet list if it exists.
        if pet in self.pets:
            self.pets.remove(pet)
        else:
            raise ValueError(f"Pet '{pet.name}' not found in {self.name}'s pet list.")

    def get_all_tasks(self) -> list[Task]:
        # Return a flat list of every task across all of this owner's pets.
        return [task for pet in self.pets for task in pet.tasks]

    def edit_info(self, name: str, preferences: dict) -> None:
        # Update the owner's name and preferences in place.
        self.name = name
        self.preferences = preferences


@dataclass
class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""
    owner: Owner
    available_minutes: int = 480
    daily_tasks: list[Task] = field(default_factory=list)
    # will not print to console, is internal variable
    _minutes_used: int = field(default=0, init=False, repr=False)

    def load_tasks_from_pet(self, pet: Pet) -> None:
        # Pull all tasks from a single pet into daily_tasks.
        for task in pet.tasks:
            self.daily_tasks.append(task)

    def load_tasks_from_owner(self) -> None:
        # Pull tasks from every pet belonging to self.owner into daily_tasks.
        # warning: overwrites any tasks already in daily_tasks rather than appending to them
        self.daily_tasks = [task for pet in self.owner.pets for task in pet.tasks]

    def add_task(self, task: Task) -> None:
        # Add a task to daily_tasks and increment _minutes_used by its duration.
        self.daily_tasks.append(task)
        self._minutes_used += task.duration_minutes

    def remove_task(self, task: Task) -> None:
        # Remove a task from daily_tasks and decrement _minutes_used by its duration.
        if task in self.daily_tasks:
            self.daily_tasks.remove(task)
            self._minutes_used -= task.duration_minutes
        else:
            raise ValueError(f"Task '{task.name}' not found in the task list.")

    def remaining_minutes(self) -> int:
        # Return available_minutes minus _minutes_used.
        return self.available_minutes - self._minutes_used

    def sort_by_priority(self) -> list[Task]:
        # Return daily_tasks sorted by Priority value (HIGH first).
        return sorted(self.daily_tasks, key=lambda task: task.priority.value, reverse=False)

    def sort_by_duration(self) -> list[Task]:
        # Return daily_tasks sorted by duration_minutes (shortest first).
        return sorted(self.daily_tasks, key=lambda task: task.duration_minutes, reverse=False)

    def generate_plan(self) -> list[Task]:
        # Sort tasks by priority, then greedily include tasks until available_minutes is exhausted.
        plan = sorted(self.daily_tasks, key=lambda task: (task.priority.value, task.duration_minutes))
        final_plan = []
        for task in plan:
            if task.duration_minutes <= self.remaining_minutes():
                final_plan.append(task)
                self._minutes_used += task.duration_minutes
        return final_plan
