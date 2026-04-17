# LLM Orchestration

## Purpose
This document translates accepted ownership boundaries into technical orchestration rules.
It defines what deterministic code controls, what LLM may generate, what Communication DNA may influence, and where validation and interpretation happen.

## Deterministic Code Controls
- canonical flow order
- artifact creation order
- process-state transitions
- resolution-status recording
- schema validation
- one-action guardrail
- one-diagnosis guardrail
- persistence of `CycleRecord` and `MemoryRecord`
- packet discipline in repository execution
- fallback activation when LLM output is unavailable or invalid

## LLM May Generate
- Russian user-facing wording of accepted artifacts
- `DiagnosisOutput` phrasing inside the diagnosis contract
- `RestructuringOutput` inside the restructuring contract
- `ActionOutput` inside the one-action contract
- bounded `ProgressSnapshot` phrasing after deterministic resolution is already fixed

## Communication DNA May Influence
- hidden-structure cues
- prohibition signals
- resistance pattern notes
- likely self-sabotage point
- phrasing constraints for diagnosis and restructuring

Communication DNA may influence diagnosis quality and phrasing quality.
It may not independently route the product flow or assign actions.

## Validation Ownership

### Code-Level Validation
Deterministic code validates:
- required fields
- scenario scope
- singular artifact constraints
- allowed state transition order
- one action only
- one leading mechanism only
- non-empty Russian-ready text fields after generation

### Module-Level Validation
Each module validates that its upstream artifact is complete enough for transformation.
This validation is bounded by the module contract and is enforced by code once implemented.

## Interpretation Ownership

### Communication DNA
Performs hidden-structure interpretation support.

### Diagnosis Module Using LLM
Performs leading mechanism interpretation and old-belief interpretation.

### Restructuring Module Using LLM
Performs admissible reframing interpretation.

### Check-In Module Using LLM
Performs bounded interpretation of the user's action outcome.

### Progress Memory
Performs bounded summary interpretation of how the cycle resolved.

## Narrow Adapter Rule
- Provider-specific LLM logic should remain inside a narrow adapter layer.
- The engine may call the adapter, but must not spread provider request logic across the rest of the runtime.
- If the adapter fails or returns invalid structure, deterministic code must switch to fallback generation without breaking the cycle.

## Guardrails Against Flow Drift
- No generated output may invent a new stage.
- No generated output may skip an accepted artifact.
- No generated output may widen the scenario beyond money/income.
- No generated output may convert the system into open-ended chat.

## Guardrails Against Multi-Action Drift
- `ActionOutput` may contain one action only.
- If generated text implies several actions, code must reject or force regeneration.
- `CheckInOutput` must refer to the assigned action, not an improvised different plan.

## Guardrails Against Diagnosis Drift
- `DiagnosisOutput` may contain one leading mechanism hypothesis only.
- Communication DNA may surface multiple cues, but diagnosis must collapse them into one current-cycle hypothesis.
- Later cycles may revisit or replace the hypothesis, but not within the same cycle artifact set.

## Processing Order
1. Validate intake scope and completeness
2. Generate `DnaSupportSignals`
3. Generate `DiagnosisOutput` through the LLM adapter or fallback
4. Generate `OldCycleMap`
5. Generate `RestructuringOutput` through the LLM adapter or fallback
6. Generate `ActionOutput` through the LLM adapter or fallback
7. Receive `CheckInOutput`
8. Generate `ProgressSnapshot` phrasing through the LLM adapter or fallback after deterministic resolution
9. Update `MemoryRecord`

## Orchestration Rule
LLM and Communication DNA operate inside deterministic product boundaries.
They do not own product meaning, flow routing, or execution authority.
