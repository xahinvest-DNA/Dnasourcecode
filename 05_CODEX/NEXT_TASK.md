# Active Packet

## Packet ID
`F-005`

## Title
Minimal Executable Restructuring Loop

## Status
Active until manager review closes the packet.

## Objective
Build the first narrow executable vertical slice of the product: one end-to-end restructuring cycle for the money/income scenario.

## In Scope
- Create one executable flow for one `CycleRecord`.
- Enforce accepted process-state order.
- Enforce one leading mechanism and one action guardrails.
- Persist cycle artifacts locally.
- Support return check-in and final resolution.
- Provide a minimal UI sufficient for manual testing.

## Out of Scope
- auth
- multi-user
- production infrastructure
- polished design
- analytics dashboard
- domain expansion
- advanced memory beyond minimum local continuity
- optimization beyond the accepted flow

## Required Deliverables
- minimal runtime entrypoint
- minimal flow orchestration
- local persistence for cycle records
- minimal user interface for starting a cycle, seeing artifacts, submitting check-in, and seeing final resolution
- tests for core flow state order and guardrails
- Supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- A user can create a cycle from intake input.
- The system generates accepted artifacts in the correct order.
- Skipped transitions are rejected.
- The system does not generate multiple actions.
- Check-in cannot resolve a cycle before action assignment.
- A completed cycle stores `ProgressSnapshot` and a non-`none` resolution status.
- The slice is runnable locally.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
