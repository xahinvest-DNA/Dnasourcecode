# Domain Model

## Core Entities
- `UserProfile` - minimal user identity and cycle history anchor
- `IntakeRecord` - structured intake capture for one cycle
- `MechanismHypothesis` - leading hidden poverty mechanism guess for the cycle
- `CycleMap` - old or new cycle represented as belief, attention, behavior, result, reinforcement
- `ActionPlan` - one bounded action with completion criteria
- `CheckInRecord` - user response after attempting the action
- `ProgressSnapshot` - short state of what shifted or repeated across cycles
- `CycleRecord` - container joining all records for one completed or active cycle

## Relationships
- One `UserProfile` can own many `CycleRecord` entries.
- One `CycleRecord` contains one `IntakeRecord`.
- One `CycleRecord` contains one leading `MechanismHypothesis`.
- One `CycleRecord` contains one old `CycleMap` and one new `CycleMap`.
- One `CycleRecord` contains one `ActionPlan`.
- One `CycleRecord` can contain zero or one `CheckInRecord` until check-in is completed.
- One `CycleRecord` ends with one `ProgressSnapshot`.

## Modeling Rule
- Preserve a single leading hypothesis and a single action per cycle in MVP.
