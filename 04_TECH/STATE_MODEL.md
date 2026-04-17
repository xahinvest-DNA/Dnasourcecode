# State Model

## Purpose
This document defines the technical state model for one restructuring cycle.
It uses the already accepted strategic status meanings and does not redefine them.

## State Axes
The cycle uses two coordinated state axes:
- `process_state` for where the current cycle is in execution
- `resolution_status` for how the cycle resolved once check-in is processed

## Process States
1. `draft`
2. `intake_ready`
3. `diagnosed`
4. `restructured`
5. `action_assigned`
6. `checkin_received`
7. `cycle_resolved`

## Resolution Statuses
- `none`
- `completed_shifted`
- `completed_partial`
- `completed_blocked`

`resolution_status` remains `none` until the cycle is resolved.

## State Meanings

### `draft`
The cycle exists but does not yet contain a valid `IntakeRecord`.

### `intake_ready`
The cycle contains a valid `IntakeRecord` and may proceed to diagnosis.

### `diagnosed`
The cycle contains `DiagnosisOutput` and `OldCycleMap`.

### `restructured`
The cycle contains `RestructuringOutput`.

### `action_assigned`
The cycle contains `ActionOutput` and is waiting for user action.

### `checkin_received`
The cycle contains `CheckInOutput` and is waiting for final resolution recording.

### `cycle_resolved`
The cycle contains `ProgressSnapshot` and has one non-`none` `resolution_status`.

## Allowed Transitions
- `draft -> intake_ready`
- `intake_ready -> diagnosed`
- `diagnosed -> restructured`
- `restructured -> action_assigned`
- `action_assigned -> checkin_received`
- `checkin_received -> cycle_resolved`

## Allowed Hold / Retry Behavior
- `draft -> draft` when intake is incomplete
- `intake_ready -> intake_ready` when diagnosis cannot be finalized yet
- `action_assigned -> action_assigned` while waiting for the user to attempt the action
- `checkin_received -> checkin_received` while progress fixation is not yet recorded

## Invalid Transitions
- `draft -> restructured`
- `draft -> action_assigned`
- `intake_ready -> action_assigned`
- `diagnosed -> action_assigned`
- `restructured -> checkin_received`
- `cycle_resolved -> diagnosed`
- Any transition that bypasses `ActionOutput` and still produces `CheckInOutput`
- Any transition that changes `resolution_status` before `checkin_received`

## Completion Boundary
A cycle reaches `cycle_resolved` only when:
- `CheckInOutput` exists
- `ProgressSnapshot` exists
- `resolution_status` is one of:
  - `completed_shifted`
  - `completed_partial`
  - `completed_blocked`

## Resolution Logic

### `completed_shifted`
Use when:
- the action was completed or meaningfully executed,
- a visible shift marker exists,
- the result supports the replacement cycle more than the old cycle.

### `completed_partial`
Use when:
- some movement happened,
- but the shift marker is weak, incomplete, or mixed,
- and the replacement cycle is not yet strongly supported.

### `completed_blocked`
Use when:
- the action was not effectively carried through or had no useful shift,
- the old cycle remained dominant,
- or the check-in shows no meaningful move away from the original loop.

## State Rules
- One cycle may have only one `process_state` at a time.
- One resolved cycle may have only one `resolution_status`.
- A cycle cannot reopen itself into a new cycle; a new cycle requires a new `cycle_id`.
