from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    priority: str
    duration_minutes: int
    category: str

    def edit_task(self, name: str, priority: str, duration_minutes: int) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_info(self, name: str, species: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        pass

    def edit_info(self, name: str, preferences: dict) -> None:
        pass


@dataclass
class Scheduler:
    daily_tasks: list[Task] = field(default_factory=list)
    available_minutes: int = 480

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass

    def sort_by_duration(self) -> list[Task]:
        pass

    def generate_plan(self) -> list[Task]:
        pass
