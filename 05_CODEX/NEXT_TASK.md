# Active Packet

## Packet ID
`F-006`

## Title
Russian LLM Intelligence Upgrade

## Status
Active until manager review closes the packet.

## Objective
Upgrade the runnable baseline from heuristic meaning generation to an LLM-backed meaning layer and make the full user-facing slice testable in Russian.

## In Scope
- Replace heuristic generation for core meaning artifacts with an LLM-backed layer where appropriate.
- Preserve deterministic guardrails and accepted state transitions.
- Fully localize the runnable user-facing slice into Russian.
- Keep a safe fallback path if LLM generation fails.
- Extend tests for guardrails, fallback, and Russian rendering.

## Out of Scope
- product-flow rewrite
- module-boundary rewrite
- domain expansion
- auth
- multi-user
- production infra
- free chat interface
- UI polish beyond Russian usability needs

## Required Deliverables
- LLM-backed runtime adapter
- Russian-localized runnable UI
- fallback generation path
- updated runtime tests for guardrails, fallback, and Russian UI basics
- Supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- The product still runs end-to-end locally.
- Russian is the full primary user-facing language.
- The user can test the whole cycle in Russian.
- Deterministic guardrails still hold.
- LLM-backed artifacts are less template-like than the heuristic baseline when the adapter is available.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
