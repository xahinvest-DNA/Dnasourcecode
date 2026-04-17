# State Model

## Cycle States
1. `new`
2. `intake_captured`
3. `diagnosis_ready`
4. `old_cycle_mapped`
5. `new_cycle_defined`
6. `action_assigned`
7. `checkin_pending`
8. `cycle_closed`

## Allowed Transitions
- `new -> intake_captured`
- `intake_captured -> diagnosis_ready`
- `diagnosis_ready -> old_cycle_mapped`
- `old_cycle_mapped -> new_cycle_defined`
- `new_cycle_defined -> action_assigned`
- `action_assigned -> checkin_pending`
- `checkin_pending -> cycle_closed`

## Failure / Hold Cases
- If intake is incomplete, remain in `new` or `intake_captured`.
- If diagnosis confidence is too weak, do not open action assignment.
- If the action is not performed, keep the cycle in `checkin_pending` with a blockage note.

## State Rule
- No state should skip directly from intake to action in MVP.
