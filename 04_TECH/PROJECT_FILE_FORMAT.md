# Project File Format

## Documentation Rules
- Use concise Markdown.
- Prefer operational headings over narrative prose.
- State files must be update-friendly and easy to diff.
- Avoid placeholders that do not carry a decision, boundary, or active fact.

## Packet File Rules
- `05_CODEX/NEXT_TASK.md` must contain exactly one active packet.
- Packets must include: packet ID, objective, scope, out-of-scope, deliverables, completion criteria, sync requirements.
- Packet language must be bounded and implementation-safe.

## Task Ledger Rules
- `05_CODEX/TASKS.md` tracks many tasks.
- Only one task may be marked active.
- Future work stays upcoming until promoted by the manager.

## Worklog Rules
- `05_CODEX/CODEX_WORKLOG.md` records only completed substantive execution steps.
- Every worklog entry ends with a recommended next step, not a self-opened next packet.

## State Sync Rule
- After every substantive packet, synchronize `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md`.
