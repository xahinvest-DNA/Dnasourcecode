# Data Schema

## `IntakeRecord`
- `cycle_id`
- `captured_at`
- `raw_problem_text`
- `problem_summary`
- `repeated_pattern_summary`
- `candidate_belief_text`
- `candidate_behavior_clues`

## `MechanismHypothesis`
- `cycle_id`
- `generated_at`
- `mechanism_label`
- `old_belief`
- `hidden_prohibition`
- `attention_bias`
- `behavior_pattern`
- `self_sabotage_risk`
- `confidence_note`

## `CycleMap`
- `cycle_id`
- `cycle_type` (`old` or `new`)
- `belief`
- `attention`
- `behavior`
- `result`
- `reinforcement`

## `ActionPlan`
- `cycle_id`
- `action_text`
- `completion_criteria`
- `timeframe`
- `risk_note`
- `assigned_at`

## `CheckInRecord`
- `cycle_id`
- `checked_in_at`
- `completion_status`
- `observed_result`
- `internal_reaction`
- `old_cycle_return_note`

## `ProgressSnapshot`
- `cycle_id`
- `snapshot_at`
- `shift_marker`
- `remaining_barrier`
- `recommended_next_focus`

## Schema Rule
- Prefer explicit fields over vague text blobs for anything that drives the next cycle.
