# Domain Model

## Purpose
This document turns accepted strategic, product, and module truth into a stable technical domain model.
It does not redefine product meaning.

## Main Entities

### `UserProfile`
The minimal technical anchor for one user's cycle history in the money/income scenario.

### `CycleRecord`
The top-level container for one restructuring cycle.
This is the main technical boundary object for MVP.

### `IntakeRecord`
The structured capture of the user's current money/income problem and repeated pattern.
Owned by the Intake module.

### `DiagnosisOutput`
The structured artifact that holds the leading hidden poverty mechanism hypothesis and the current old-belief logic.
Owned by the Mechanism Diagnosis module.

### `OldCycleMap`
The structured representation of the current cycle:
`belief -> attention -> behavior -> result -> reinforcement`
Owned by the product flow stage "Old Cycle Presentation", but stored inside the `CycleRecord`.

### `RestructuringOutput`
The structured replacement-cycle artifact.
Owned by the Cycle Restructuring module.

### `ActionOutput`
The one bounded action artifact for the cycle.
Owned by the Micro Action Engine.

### `CheckInOutput`
The structured result of the user returning after the action attempt.
Owned by the Check-In Engine.

### `ProgressSnapshot`
The structured record of how the cycle resolved.
Owned by the Progress Memory module.

### `DnaSupportSignals`
The structured diagnostic-support output from Communication DNA.
This supports diagnosis but is not the final diagnosis artifact.

### `MemoryRecord`
The accumulated memory view across completed or attempted cycles.
This is not a separate product stage; it is the stored continuity layer.

## Cycle-Level Object Boundary
One `CycleRecord` contains exactly one instance of:
- `IntakeRecord`
- `DiagnosisOutput`
- `OldCycleMap`
- `RestructuringOutput`
- `ActionOutput`
- `CheckInOutput` when the user has returned
- `ProgressSnapshot` when the cycle has been resolved

It may also contain:
- one `DnaSupportSignals` artifact
- links to prior cycle summaries from `MemoryRecord`

## Relationships
- One `UserProfile` owns many `CycleRecord` entries.
- One `MemoryRecord` aggregates summaries of prior `CycleRecord` entries for one `UserProfile`.
- One `CycleRecord` may reference zero or more prior cycle summaries for context.
- `DiagnosisOutput` may be informed by `DnaSupportSignals`, but it is not replaced by it.
- `RestructuringOutput` depends on `DiagnosisOutput` and `OldCycleMap`.
- `ActionOutput` depends on `RestructuringOutput`.
- `CheckInOutput` depends on `ActionOutput`.
- `ProgressSnapshot` depends on the full current-cycle artifact set plus prior memory when needed.

## Artifact Ownership

| Artifact | Owner |
| --- | --- |
| `IntakeRecord` | Intake module |
| `DnaSupportSignals` | Communication DNA layer |
| `DiagnosisOutput` | Mechanism Diagnosis module |
| `OldCycleMap` | Old Cycle Presentation stage, stored in cycle record |
| `RestructuringOutput` | Cycle Restructuring module |
| `ActionOutput` | Micro Action Engine |
| `CheckInOutput` | Check-In Engine |
| `ProgressSnapshot` | Progress Memory module |

## Technical Modeling Rules
- Preserve one leading mechanism hypothesis per cycle.
- Preserve one bounded action per cycle.
- Preserve one resolution status per cycle.
- Preserve one top-level `CycleRecord` as the main persistence boundary for MVP.
- Do not create technical objects that imply multi-branch flow or multi-action flow.
