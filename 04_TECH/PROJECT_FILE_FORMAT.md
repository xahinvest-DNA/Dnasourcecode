# Project File Format

## Purpose
This document defines project-facing documentation and packet format rules that future implementation packets must follow.

## Packet Structure Expectations
Every execution packet in `05_CODEX/NEXT_TASK.md` must contain:
- `Packet ID`
- `Title`
- `Status`
- `Objective`
- `In Scope`
- `Out of Scope`
- `Required Deliverables`
- `Completion Criteria`
- `Sync Requirement`

## Packet Discipline Rules
- Only one packet may be active or execution-ready at a time.
- A packet must be bounded to one reviewable slice.
- A packet must not silently redefine accepted strategic, product, module, or tech truth.
- If a contradiction is discovered, it must be stated explicitly rather than patched implicitly.

## State Sync Expectations
After every substantive packet, synchronize:
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/CODEX_WORKLOG.md`

If truth ownership changes, also synchronize:
- `01_MASTER/SSOT_MAP.md`

## Artifact Naming Discipline
Use the accepted artifact names exactly:
- `Intake Record`
- `DNA Support Signals`
- `Diagnosis Output`
- `Old Cycle Map`
- `Restructuring Output`
- `Action Output`
- `Check-In Output`
- `Progress Snapshot`
- `Cycle Record`
- `Memory Record`

Do not introduce alternate names for the same artifact in later packets unless manager-approved.

## Documentation Consistency Rules
- Strategic documents define meaning, not schemas.
- Product documents define flow and user-facing artifact chain, not runtime implementation.
- Module documents define ownership and hand-offs, not product strategy.
- Tech documents define technical formalization, not new product meaning.
- Codex control documents define execution state, not product truth.

## Execution Packet Writing Rules
- Deliverables must point to concrete files.
- Completion criteria must be objectively checkable.
- Scope must exclude unrelated implementation work.
- Notes about future work belong in `TASKS.md` or `CODEX_WORKLOG.md`, not hidden in packet scope.

## Worklog Entry Rules
Each `CODEX_WORKLOG.md` entry should state:
- packet ID
- result
- created or updated files
- state sync performed
- contradictions found or not found
- recommended next step

## Technical Consistency Rule
Future implementation packets must use the accepted artifact names, cycle boundaries, and ownership rules from the current tech layer unless a later manager-approved packet changes them explicitly.
