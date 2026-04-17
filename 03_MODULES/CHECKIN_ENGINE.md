# Check-In Engine

## Purpose
Convert the user's return report after the assigned action into one `Check-In Output` that states what happened in the current cycle.

## Upstream Input
- `Action Output`
- User completion report
- Observed external result
- Observed internal reaction

## Owned Transformation
- Determine whether the action was completed, partial, or not completed
- Capture the observed result in relation to the action
- Capture the internal reaction in relation to the action
- Note whether the old cycle reappeared

## Validation
- Confirm the check-in refers to the assigned action
- Confirm enough evidence exists to determine completion status
- Confirm the output stays within the current cycle

## Interpretation
- Limited to interpreting the reported outcome against the assigned action and current cycle
- Does not create a new diagnosis
- Does not generate a new restructuring

## Output Artifact
`Check-In Output`

### Required Fields
- completion status
- observed external result
- observed internal reaction
- old-cycle return note

## Exit Condition
- The current cycle has one clear post-action status artifact ready for progress fixation

## Must Not Do
- Open a new cycle
- Assign a new action
- Rewrite the diagnosis
- Drift into long-form reflective journaling

## Boundary Rule
- Check-in owns current-cycle evidence only.
- Check-in does not open a new cycle.
