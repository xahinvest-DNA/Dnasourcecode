# Current State

## Status
- Date: 2026-04-17
- Active frontier: `F-004 Tech Model Fixation`
- Current repository role: documentation-first source-of-truth and execution control system
- Runtime status: no product runtime, backend, or app implementation is opened yet

## What Is Already Fixed
- The repository follows a source-of-truth operating model rather than a loose file dump.
- The execution model is manager-led: ChatGPT selects direction and packet boundaries; Codex executes bounded packets and synchronizes repository state.
- The product is a trainer, not an affirmation app.
- The initial domain is hidden poverty mechanism restructuring for the money/income scenario.
- The core product loop is `belief -> attention -> behavior -> result -> reinforcement`.
- The system architecture is layered: deterministic code + LLM + Communication DNA.
- One bounded micro-action per cycle is mandatory.
- One completed restructuring cycle is the core unit of user value.

## Current Repository Reality
- The repository brain skeleton has been initialized from the accepted transcript context.
- Product framing has been tightened from initial depth into one canonical MVP money/income flow.
- Screen ownership and product-stage artifacts are explicit across the product layer.
- Module boundaries and module-owned artifacts are now fixed without changing the canonical MVP flow.
- Validation versus interpretation is explicitly separated at the module layer.
- A strategic product-structure layer now defines mechanism, cycle, completed value unit, memory boundaries, and intelligence-layer ownership.
- The tech layer now formalizes accepted entities, artifact schemas, cycle state logic, orchestration rules, and project-facing packet/file discipline.
- Codex execution rules, active packet discipline, and handoff structure are now explicit.
- `F-003` and `F-003a` are complete.
- `F-004` is complete from the Codex side and awaiting manager review.

## Open Items
- Confirm the preferred external product naming for user-facing language.
- Define the first executable vertical slice in `F-005` without changing accepted product meaning.
- Decide the first runtime stack only after `F-005` scope is fixed.

## Next Step
- Manager review of `F-004 Tech Model Fixation`.
- If accepted, open `F-005 First MVP Flow Packet`.

## Execution Model
- ChatGPT owns direction, prioritization, packet definition, and final decision-making.
- Codex owns bounded execution, repository synchronization, and structured handoff.
- State files must remain synchronized after every substantive packet.
