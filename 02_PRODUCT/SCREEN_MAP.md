# Screen Map

## Canonical Screen Sequence

| Screen | Stage Owner | Screen Purpose | Required Input | Primary Output | Screen Boundary |
| --- | --- | --- | --- | --- | --- |
| `S-01 Entry` | Entry | Frame the product correctly before any analysis starts | User arrives with a money/income problem | Entry confirmation | Does not diagnose, advise, or collect history |
| `S-02 Intake` | Intake | Capture the live problem and repeated pattern in natural language | Entry confirmation | Intake record | Does not conclude the mechanism |
| `S-03 Diagnosis` | Mechanism Diagnosis | Present one leading hidden poverty mechanism hypothesis | Intake record | Diagnosis output | Does not present the full old cycle or new cycle |
| `S-04 Old Cycle` | Old Cycle Presentation | Show how the current cycle keeps reproducing the same outcome | Diagnosis output | Old cycle map | Does not generate the new belief or the action |
| `S-05 New Cycle` | New Cycle Construction | Define one admissible replacement cycle | Diagnosis output and old cycle map | Restructuring output | Does not assign the action |
| `S-06 One Action` | One Micro-Action | Convert restructuring into one real-world test step | Restructuring output | Action output | Does not re-diagnose or open multiple actions |
| `S-07 Check-In` | Check-In | Capture what happened after the action | Action output and user return | Check-in output | Does not open a new cycle |
| `S-08 Progress` | Progress Fixation | Record the result of the cycle and show the current status | Check-in output | Progress snapshot | Does not generate the next packet |

## Screen Ownership Rules
- Each screen owns one stage only.
- Each screen emits one primary output only.
- If a screen needs to emit two independent outputs, the flow is underspecified and must be split in F-003.
- Screens may show supporting context from previous steps, but they may not take over another screen's primary responsibility.

## Required Hand-Offs
- `S-01 -> S-02`: entry confirmation
- `S-02 -> S-03`: intake record
- `S-03 -> S-04`: diagnosis output
- `S-04 -> S-05`: old cycle map
- `S-05 -> S-06`: restructuring output
- `S-06 -> S-07`: action output
- `S-07 -> S-08`: check-in output

## MVP Screen Constraint
- All screens exist for the money/income scenario only.
- No optional side screens, detours, dashboards, or educational branches are part of the canonical MVP flow.
