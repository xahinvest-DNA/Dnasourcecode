# Micro Action Engine

## Purpose
Convert the `Restructuring Output` into one bounded `Action Output` that can be attempted in the real world and checked later.

## Upstream Input
- `Restructuring Output`
- User constraints and context
- Prior completion history when relevant

## Owned Transformation
- Select one concrete action that tests the new cycle
- Define the completion criterion
- Define the timeframe
- Add one failure-risk note when needed

## Validation
- Confirm the action is singular
- Confirm the action can be completed or clearly failed
- Confirm the action matches the new behavior direction
- Confirm the output contains no new diagnosis

## Interpretation
- Limited to translating the replacement cycle into one practical test step
- Does not reinterpret the hidden mechanism
- Does not rewrite the new belief unless the restructuring artifact is invalid

## Output Artifact
`Action Output`

### Required Fields
- action
- completion criterion
- timeframe

### Optional Field
- failure-risk note

## Exit Condition
- One bounded action exists and can be taken into check-in without additional planning

## Must Not Do
- Produce an action list
- Re-diagnose the mechanism
- Open a new cycle
- Turn into a broad plan or habit system

## Boundary Rule
- The action module owns one action only.
- The action module does not re-diagnose.
