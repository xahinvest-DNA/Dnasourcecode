# Progress Memory Module

## Purpose
Record the result of the current cycle and store the minimum historical context needed for future cycles.

## Upstream Input
- `Intake Record`
- `Diagnosis Output`
- `Old Cycle Map`
- `Restructuring Output`
- `Action Output`
- `Check-In Output`

## Owned Transformation
- Write the completed or partial cycle record
- Produce the current `Progress Snapshot`
- Mark repeated mechanism patterns when visible across history
- Mark remaining barrier for future reference

## Validation
- Confirm the current cycle artifacts are internally consistent
- Confirm the progress record refers to the current cycle only
- Confirm the module records the result instead of redefining product direction

## Interpretation
- Limited to pattern recording and status summarization across cycle history
- Does not define product flow
- Does not define the next manager packet

## Output Artifact
`Progress Snapshot`

### Required Fields
- cycle status
- shift marker
- remaining barrier

### Stored History Role
- Preserve cycle history for future diagnosis and action calibration
- Preserve repeated mechanism markers

## Exit Condition
- The current cycle is recorded and future modules can reference its stored outcome

## Must Not Do
- Open the next packet
- Create a new diagnosis
- Define a new action
- Expand into broad analytics beyond MVP

## Boundary Rule
- Progress memory records cycle result but does not define the next packet.
