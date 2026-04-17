# Data Schema

## Purpose
This document defines the first stable schema shape for accepted MVP artifacts.
The goal is implementation-readiness without changing product meaning.

## `UserProfile`
- `user_id`
- `scenario_scope` (`money_income` only in MVP)
- `created_at`
- `latest_cycle_id`
- `memory_record_id`

## `MemoryRecord`
- `memory_record_id`
- `user_id`
- `cycle_count`
- `last_mechanism_label`
- `repeated_mechanism_markers[]`
- `repeated_barrier_markers[]`
- `shift_history[]`
- `last_resolution_status`
- `updated_at`

## `CycleRecord`
- `cycle_id`
- `user_id`
- `scenario_scope`
- `process_state`
- `resolution_status`
- `created_at`
- `updated_at`
- `intake_record`
- `dna_support_signals`
- `diagnosis_output`
- `old_cycle_map`
- `restructuring_output`
- `action_output`
- `checkin_output`
- `progress_snapshot`

## `IntakeRecord`
- `artifact_id`
- `cycle_id`
- `captured_at`
- `problem_summary`
- `repeated_pattern_summary`
- `candidate_belief_language[]`
- `candidate_behavior_clues[]`
- `intake_completeness_flag`
- `source_excerpt` optional

## `DnaSupportSignals`
- `artifact_id`
- `cycle_id`
- `generated_at`
- `hidden_structure_cues[]`
- `prohibition_signals[]`
- `resistance_pattern_notes[]`
- `likely_self_sabotage_point`
- `phrasing_constraints[]`

## `DiagnosisOutput`
- `artifact_id`
- `cycle_id`
- `generated_at`
- `leading_mechanism_hypothesis`
- `old_belief_statement`
- `attention_bias_clue`
- `behavior_pattern_clue`
- `reinforcement_logic`
- `hidden_prohibition_statement` optional
- `diagnosis_confidence_note`

## `OldCycleMap`
- `artifact_id`
- `cycle_id`
- `mapped_at`
- `belief`
- `attention`
- `behavior`
- `result`
- `reinforcement`

## `RestructuringOutput`
- `artifact_id`
- `cycle_id`
- `generated_at`
- `new_belief`
- `new_attention_target`
- `new_behavior_direction`
- `desired_result_marker`
- `new_reinforcement_statement`

## `ActionOutput`
- `artifact_id`
- `cycle_id`
- `generated_at`
- `action`
- `completion_criterion`
- `timeframe`
- `failure_risk_note` optional

## `CheckInOutput`
- `artifact_id`
- `cycle_id`
- `captured_at`
- `completion_status`
- `observed_external_result`
- `observed_internal_reaction`
- `old_cycle_return_note`

## `ProgressSnapshot`
- `artifact_id`
- `cycle_id`
- `recorded_at`
- `resolution_status`
- `shift_marker`
- `remaining_barrier`
- `memory_update_note`

## Schema Constraints
- Every artifact must carry `cycle_id`.
- `scenario_scope` must remain `money_income` in MVP.
- `CycleRecord` may exist before all nested artifacts exist, but artifact slots must remain singular.
- No schema shape may imply multiple diagnoses, multiple restructuring outputs, or multiple actions in one cycle.
