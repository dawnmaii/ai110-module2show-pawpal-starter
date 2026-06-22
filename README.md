# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
========================================
  Today's Schedule for Dawn
========================================
  08:00  Medication             5 min  [high]
  08:05  Feeding               10 min  [high]
  08:15  Morning walk          30 min  [high]
  08:45  Grooming brush        15 min  [medium]
  09:00  Enrichment toy        20 min  [low]
----------------------------------------
  Total: 80 / 120 min used
  
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests/test_pawpal.py::TestMarkComplete::test_starts_incomplete PASSED     [  1%]
tests/test_pawpal.py::TestMarkComplete::test_sets_completed_true PASSED   [  3%]
tests/test_pawpal.py::TestMarkComplete::test_idempotent PASSED            [  4%]
tests/test_pawpal.py::TestNextOccurrence::test_daily_advances_one_day PASSED [  6%]
tests/test_pawpal.py::TestNextOccurrence::test_weekly_advances_seven_days PASSED [  7%]
tests/test_pawpal.py::TestNextOccurrence::test_as_needed_returns_none PASSED [  9%]
tests/test_pawpal.py::TestNextOccurrence::test_next_occurrence_starts_incomplete PASSED [ 11%]
tests/test_pawpal.py::TestNextOccurrence::test_next_occurrence_is_new_object PASSED [ 12%]
tests/test_pawpal.py::TestNextOccurrence::test_next_occurrence_inherits_all_fields PASSED [ 14%]
tests/test_pawpal.py::TestEditTask::test_updates_all_fields PASSED        [ 15%]
tests/test_pawpal.py::TestEditTask::test_none_due_date_leaves_it_unchanged PASSED [ 17%]
tests/test_pawpal.py::TestEditTask::test_explicit_due_date_updates_it PASSED [ 19%]
tests/test_pawpal.py::TestPetAddTask::test_add_increases_count PASSED     [ 20%]
tests/test_pawpal.py::TestPetAddTask::test_add_multiple_distinct_tasks PASSED [ 22%]
tests/test_pawpal.py::TestPetAddTask::test_duplicate_incomplete_task_raises PASSED [ 23%]
tests/test_pawpal.py::TestPetAddTask::test_completed_original_allows_same_name PASSED [ 25%]
tests/test_pawpal.py::TestPetAddTask::test_adding_to_empty_pet PASSED     [ 26%]
tests/test_pawpal.py::TestPetRemoveTask::test_remove_decreases_count PASSED [ 28%]
tests/test_pawpal.py::TestPetRemoveTask::test_remove_nonexistent_raises PASSED [ 30%]
tests/test_pawpal.py::TestPetRemoveTask::test_removes_by_identity_not_equality PASSED [ 31%]
tests/test_pawpal.py::TestPetRemoveTask::test_removes_correct_task_among_multiple PASSED [ 33%]
tests/test_pawpal.py::TestPetEditInfo::test_updates_name_and_species PASSED [ 34%]
tests/test_pawpal.py::TestOwnerAddPet::test_add_increases_count PASSED    [ 36%]
tests/test_pawpal.py::TestOwnerAddPet::test_duplicate_name_raises PASSED  [ 38%]
tests/test_pawpal.py::TestOwnerAddPet::test_same_name_different_species_still_raises PASSED [ 39%]
tests/test_pawpal.py::TestOwnerAddPet::test_add_multiple_distinct_pets PASSED [ 41%]
tests/test_pawpal.py::TestOwnerGetAllTasks::test_no_pets_returns_empty PASSED [ 42%]
tests/test_pawpal.py::TestOwnerGetAllTasks::test_pet_with_no_tasks_returns_empty PASSED [ 44%]
tests/test_pawpal.py::TestOwnerGetAllTasks::test_flattens_tasks_from_multiple_pets PASSED [ 46%]
tests/test_pawpal.py::TestOwnerGetAllTasks::test_includes_completed_tasks PASSED [ 47%]
tests/test_pawpal.py::TestOwnerEditInfo::test_updates_name_and_preferences PASSED [ 49%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_loads_incomplete_tasks PASSED [ 50%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_skips_completed_tasks PASSED [ 52%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_identity_guard_prevents_double_load PASSED [ 53%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_conflict_higher_priority_displaces_lower PASSED [ 55%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_conflict_equal_priority_keeps_both PASSED [ 57%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_conflict_lower_priority_incoming_is_skipped PASSED [ 58%]
tests/test_pawpal.py::TestLoadTasksFromPet::test_medium_displaces_low_keeps_high PASSED [ 60%]
tests/test_pawpal.py::TestLoadTasksFromOwner::test_loads_all_pets PASSED  [ 61%]
tests/test_pawpal.py::TestLoadTasksFromOwner::test_reload_does_not_duplicate PASSED [ 63%]
tests/test_pawpal.py::TestLoadTasksFromOwner::test_owner_with_no_pets PASSED [ 65%]
tests/test_pawpal.py::TestSchedulerRemoveTask::test_remove_decreases_count PASSED [ 66%]
tests/test_pawpal.py::TestSchedulerRemoveTask::test_remove_nonexistent_raises PASSED [ 68%]
tests/test_pawpal.py::TestSchedulerRemoveTask::test_removes_by_identity PASSED [ 69%]
tests/test_pawpal.py::TestGeneratePlan::test_empty_pool_returns_empty PASSED [ 71%]
tests/test_pawpal.py::TestGeneratePlan::test_tasks_that_fit_are_included PASSED [ 73%]
tests/test_pawpal.py::TestGeneratePlan::test_task_exceeding_budget_is_excluded PASSED [ 74%]
tests/test_pawpal.py::TestGeneratePlan::test_exactly_fitting_task_is_included PASSED [ 76%]
tests/test_pawpal.py::TestGeneratePlan::test_completed_tasks_excluded PASSED [ 77%]
tests/test_pawpal.py::TestGeneratePlan::test_minutes_used_tracked PASSED  [ 79%]
tests/test_pawpal.py::TestGeneratePlan::test_generate_plan_resets_minutes_used_on_second_call PASSED [ 80%]
tests/test_pawpal.py::TestGeneratePlan::test_sort_by_priority_high_first PASSED [ 82%]
tests/test_pawpal.py::TestGeneratePlan::test_sort_by_duration_shortest_first PASSED [ 84%]
tests/test_pawpal.py::TestGeneratePlan::test_sort_by_both_priority_then_duration PASSED [ 85%]
tests/test_pawpal.py::TestGeneratePlan::test_greedy_skips_oversize_fits_smaller_later PASSED [ 87%]
tests/test_pawpal.py::TestGeneratePlan::test_remaining_minutes_after_plan PASSED [ 88%]
tests/test_pawpal.py::TestSortHelpers::test_sort_by_priority_all_levels PASSED [ 90%]
tests/test_pawpal.py::TestSortHelpers::test_sort_by_duration_ascending PASSED [ 92%]
tests/test_pawpal.py::TestRecurringTaskFlow::test_completing_and_adding_next_daily PASSED [ 93%]
tests/test_pawpal.py::TestRecurringTaskFlow::test_completing_and_adding_next_weekly PASSED [ 95%]
tests/test_pawpal.py::TestRecurringTaskFlow::test_as_needed_produces_no_next_occurrence PASSED [ 96%]
tests/test_pawpal.py::TestRecurringTaskFlow::test_adding_same_next_occurrence_twice_raises PASSED [ 98%]
tests/test_pawpal.py::TestRecurringTaskFlow::test_recurring_task_chain_across_scheduler PASSED [100%]

============================== 63 passed in 0.43s ==============================

```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
