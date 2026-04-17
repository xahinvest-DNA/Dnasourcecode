# Active Packet

## Packet ID
`F-003`

## Title
Module Boundary Fixation

## Status
Active until manager review closes the packet.

## Objective
Convert the accepted product-layer framing into formal module boundaries and contracts without changing the canonical MVP flow.

## In Scope
- Freeze the responsibility of each module.
- Define explicit module inputs and outputs.
- Define where validation happens and where interpretation happens.
- Clarify the exact role of the Communication DNA layer inside diagnosis support.
- Synchronize supporting state files after module-layer work.

## Out of Scope
- Product runtime
- Backend implementation
- Screen redesign
- Changes to canonical MVP flow unless an actual contradiction is found
- Non-money scenarios

## Required Deliverables
- `03_MODULES/INTAKE.md`
- `03_MODULES/MECHANISM_DIAGNOSIS.md`
- `03_MODULES/CYCLE_RESTRUCTURING.md`
- `03_MODULES/MICRO_ACTION_ENGINE.md`
- `03_MODULES/CHECKIN_ENGINE.md`
- `03_MODULES/PROGRESS_MEMORY.md`
- `03_MODULES/COMMUNICATION_DNA_LAYER.md`
- Supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- Module responsibilities are explicit.
- Module input/output contracts are explicit.
- Validation versus interpretation ownership is explicit.
- The module layer is ready for `F-004 Tech Model Fixation`.
- Supporting state files are synchronized.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
