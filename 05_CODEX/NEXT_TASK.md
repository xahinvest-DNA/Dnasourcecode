# Active Packet

## Packet ID
`F-004`

## Title
Tech Model Fixation

## Status
Awaiting manager review before execution.

## Objective
Formalize the technical model on top of the accepted strategic structure, product flow, and module contracts without changing their meaning.

## In Scope
- Formalize domain model.
- Formalize data schema.
- Formalize state model.
- Formalize orchestration rules and structured outputs.
- Preserve accepted strategic, product, and module meaning.

## Out of Scope
- Product runtime
- Backend implementation
- Screen redesign
- Reinterpretation of mechanism, cycle, memory boundary, or intelligence ownership
- Non-money scenarios

## Required Deliverables
- `04_TECH/DOMAIN_MODEL.md`
- `04_TECH/DATA_SCHEMA.md`
- `04_TECH/STATE_MODEL.md`
- `04_TECH/LLM_ORCHESTRATION.md`
- `04_TECH/PROJECT_FILE_FORMAT.md`
- Supporting state sync in `01_MASTER/CURRENT_STATE.md`, `05_CODEX/TASKS.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/CODEX_WORKLOG.md`

## Completion Criteria
- Technical model can be built without changing strategic/product/module meaning.
- Domain, data, state, and orchestration truth are explicit.
- Supporting state files are synchronized after execution.

## Sync Requirement
- Do not open the next packet independently.
- Begin only after manager review confirms the current repository truth is sufficient.
