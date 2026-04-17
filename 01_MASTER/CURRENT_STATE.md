# Current State

## Status
- Date: 2026-04-17
- Active frontier: `F-002 Product Framing`
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
- Codex execution rules, active packet discipline, and handoff structure are now explicit.
- The active packet is `F-002` and reflects tightened product framing awaiting manager review.

## Open Items
- Confirm the preferred external product naming for user-facing language.
- Fix module interfaces and structured outputs at implementation-ready depth in `F-003`.
- Convert product-stage artifacts into formal module contracts.
- Choose the first executable vertical slice after the documentation phases.
- Decide the first runtime stack only after `F-004 Tech Model Fixation`.

## Next Step
- Manager review of `F-002 Product Framing`.
- If accepted, open `F-003 Module Boundary Fixation` as the next bounded packet.

## Execution Model
- ChatGPT owns direction, prioritization, packet definition, and final decision-making.
- Codex owns bounded execution, repository synchronization, and structured handoff.
- State files must remain synchronized after every substantive packet.
