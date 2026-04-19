# Active Packet

## Packet ID
`F-009`

## Title
Communication DNA Quality Uplift

## Status
Active until manager review closes the packet.

## Objective
Strengthen Communication DNA as a diagnostic support layer for still-weak nearby money/income mechanism distinctions.

## In Scope
- Improve DNA support signals specifically for weak nearby mechanism distinctions.
- Keep Communication DNA inside its accepted support role.
- Strengthen the signal quality passed into diagnosis without changing module ownership.
- Add regression tests for still-confusable mechanism pairs.
- Measure whether stronger DNA support improves live-vs-fallback behavior on the targeted cases.

## Out of Scope
- product-flow rewrite
- module-boundary rewrite
- domain expansion
- auth
- multi-user
- production infra
- free chat interface
- major UI redesign
- module rewrite
- state-model rewrite
- large prompt-system redesign outside the targeted weak distinctions

## Required Deliverables
- one targeted DNA review document with before/after findings
- improved DNA support generation for the targeted weak cases
- updated regression tests
- supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- The targeted weak DNA cases are retested.
- Communication DNA support quality improves on the targeted nearby mechanism distinctions.
- Deterministic guardrails still hold.
- Repeated weak distinction points have regression coverage.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
