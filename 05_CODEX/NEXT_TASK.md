# Active Packet

## Packet ID
`F-008`

## Title
Live LLM Calibration Pass

## Status
Active until manager review closes the packet.

## Objective
Validate and calibrate the live LLM-backed meaning layer against the accepted Russian real-case set.

## In Scope
- Re-run the accepted 8 Russian money/income cases with live LLM enabled.
- Compare live outputs versus fallback outputs for diagnosis, restructuring, action quality, and drift.
- Identify repeated live LLM failure modes.
- Tighten prompts and bounded validation rules where needed.
- Preserve deterministic guardrails and fallback safety.

## Out of Scope
- product-flow rewrite
- module-boundary rewrite
- domain expansion
- auth
- multi-user
- production infra
- free chat interface
- major UI redesign
- DNA-layer redesign
- widening beyond meaning-quality calibration

## Required Deliverables
- one live-vs-fallback review document summarizing findings
- updated prompts where needed
- updated bounded validation rules where needed
- updated tests for repeated live failure modes
- supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- The accepted 8 Russian money/income cases are tested live.
- The strongest repeated live failure modes lead to concrete prompt or validation improvements.
- Deterministic guardrails still hold.
- Repeated live weak points have regression coverage.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Leave this packet active for manager review after execution.
