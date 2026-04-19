# Active Packet

## Packet ID
`F-007`

## Title
Real Case Quality Pass

## Status
Active until manager review closes the packet.

## Objective
Use the accepted Russian runnable slice to improve real product quality through 5-10 grounded Russian money/income cases and targeted refinement.

## In Scope
- Run and document grounded Russian money/income cases against the accepted cycle.
- Identify weak diagnosis, restructuring, and action patterns.
- Tighten prompts and bounded generation rules without changing artifact contracts.
- Strengthen action-quality and diagnosis-consistency guardrails where needed.
- Add regression tests for the most important discovered weak points.

## Out of Scope
- product-flow rewrite
- module-boundary rewrite
- domain expansion
- auth
- multi-user
- production infra
- free chat interface
- major UI redesign
- widening beyond the accepted cycle

## Required Deliverables
- one quality review document or worklog section summarizing real-case findings
- improved prompts or generation logic
- stronger action-quality constraints
- updated tests for repeated weak points
- supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- 5-10 real Russian money/income cases are documented.
- The strongest weak patterns lead to concrete prompt, routing, or guardrail improvements.
- Deterministic guardrails still hold.
- Repeated weak points have regression coverage.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
