# Intake Module

## Purpose
Convert the user's raw money/income problem statement into a valid `Intake Record` that is ready for diagnosis.

## Upstream Input
- Entry confirmation
- Raw user description of the current money/income problem
- Raw user description of the repeated pattern
- Optional desired shift stated in user language

## Owned Transformation
- Capture the live situation in structured form
- Normalize the raw description into a concise problem summary
- Extract repeated-pattern clues without naming a mechanism
- Extract candidate belief language and candidate behavior clues for downstream use

## Validation
- Confirm the input is within the money/income scenario
- Confirm enough signal exists to attempt one diagnosis
- Confirm the record contains current problem plus repeated pattern

## Interpretation
- Limited to summarizing and structuring the user's statement
- Does not decide what the hidden mechanism is
- Does not decide what the old belief actually means

## Output Artifact
`Intake Record`

### Required Fields
- problem summary
- repeated pattern summary
- candidate belief language
- candidate behavior clues
- intake completeness flag

## Exit Condition
- A complete `Intake Record` exists and can be handed to diagnosis without further reframing

## Must Not Do
- Diagnose the hidden mechanism
- Produce an old cycle map
- Offer a new belief
- Assign an action
- Expand into non-money scenarios

## Boundary Rule
- Intake owns structured capture only.
- Intake does not diagnose.
