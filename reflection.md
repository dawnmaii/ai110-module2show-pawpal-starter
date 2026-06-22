# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  Initial UML design should allow the user to at minimum add tasks with duration and priority, schedule said tasks, and add a pet.

- What classes did you include, and what responsibilities did you assign to each?
  
  - Owner class
    - hold: owner name, pets owned by Owner, owner preferences for pet
    - perform: add/edit owner information
  
  - Pet class
    - hold: pet name, pet tasks
    - perform: add/edit pet information
  
  - Task class
    - hold: task name, task priority, task duration
    - perform: add/edit task information
  
  - Scheduler class 
    - hold: tasks to be done for the day
    - perform: add/remove tasks, sort based on priority or duration, plan generation

**b. Design changes**

- Did your design change during implementation?
  Yes, I prompted the AI to look for any missing relationships and logic bottlenecks, then reviewed the suggestions.

- If yes, describe at least one change and why you made it.
  I decided to create a Priority class in order for the Scheduler class to properly sort by priority on tasks. I also added methods for the scheduler to also update the tasks presented after a sort, and to keep a running total on time spent on tasks so we don't exceed the given limit.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  My scheduler considers the duration of the task and its priority.

- How did you decide which constraints mattered most?
  I decided based on ease of implementing/code feasibility based on what I already had for the class skeletons.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  For now, my scheduler ignores preferences. Sorting and plan generation are for task duration and priority only.

- Why is that tradeoff reasonable for this scenario?
  I find it reasonable because I have little idea of how a "preference" would be presented in the data. Would it be a note to store in a list? Should I have an exhaustive list of preferences that seem predictable? What types of preferences can there be? So far I have no way of reasonably accounting for all of these without implementing advanced logic for the scheduler, which will take additional planning and a major UML update. So preferences are display-only for now.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used AI to rigorously review the UML diagram and class skeletons for missing relationships and logic bottlenecks before implementing the code.

- What kinds of prompts or questions were most helpful?
  I think repeating the same detailed prompt (asking it to re-check) was pretty insightful, as the AI came up with new findings every time that I didn't see initially. Clarifying questions on why the AI named something it did was also helpful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  For the Pet class, I had a method to remove a pet's tasks. But I implemented it in such a way that if I removed a task on an empty task list, we'd get a ValueError. The AI suggested I keep the implementation as is and provide an inline comment noting the error.

- How did you evaluate or verify what the AI suggested?
  I wanted to handle the case where such behavior occurred via an if/else statement so the method could throw an error message at least. I evaluated it by taking a quick look at the edut, rejecting it, and then implementing the if/else branch. I had AI refine it at the end for cleanliness.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  

- Why were these tests important?
  


**b. Confidence**

- How confident are you that your scheduler works correctly?
  

- What edge cases would you test next if you had more time?
  


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  
