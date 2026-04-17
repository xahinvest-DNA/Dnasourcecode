# MVP App Structure

## Canonical Structure
The MVP is a linear mini-app with one canonical path and one canonical artifact chain.

## Artifact Chain
`Entry Confirmation -> Intake Record -> Diagnosis Output -> Old Cycle Map -> Restructuring Output -> Action Output -> Check-In Output -> Progress Snapshot`

## App Sections

| Order | Section | Owned Artifact | Purpose |
| --- | --- | --- | --- |
| 1 | Entry | Entry confirmation | Put the user into the correct money/income trainer frame |
| 2 | Intake | Intake record | Capture the current problem and repeating pattern |
| 3 | Diagnosis | Diagnosis output | Select one leading hidden poverty mechanism |
| 4 | Old Cycle | Old cycle map | Show the self-reinforcing loop |
| 5 | New Cycle | Restructuring output | Define one admissible replacement cycle |
| 6 | One Action | Action output | Translate restructuring into one bounded real-world step |
| 7 | Check-In | Check-in output | Gather evidence after the attempted action |
| 8 | Progress | Progress snapshot | Fix the cycle result and current status |

## Session Split

### Initial Session
- Entry
- Intake
- Diagnosis
- Old Cycle
- New Cycle
- One Action

### Return Session
- Check-In
- Progress

## Structural Rules
- The MVP is not a general chat shell.
- The MVP is not a content library.
- The MVP is not a multi-path coaching journey.
- Each section exists only because it produces one required artifact for the next section.
- If a section cannot be tied to one artifact, it is not fixed enough for implementation planning.

## Ready-for-F-003 Signal
This product layer is ready for module boundary fixation when each owned artifact can be turned into a module input/output contract without changing the canonical flow.
