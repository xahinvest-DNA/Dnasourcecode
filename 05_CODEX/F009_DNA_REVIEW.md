# F-009 DNA Review

## Scope
- Packet: `F-009 Communication DNA Quality Uplift`
- Date: 2026-04-19
- Focus zone: nearby money/income mechanisms where value-giving, delay, and money avoidance overlap
- Target distinction:
  - `free_value_leakage`
  - `deferred_money_conversation`
  - adjacent overlap cases around late paid transition after unpaid value

## DNA Logic Changes
- Added explicit DNA detection for early free-value leakage before the paid boundary.
- Added explicit DNA detection for delayed money conversation under the cover of proving value more.
- Added overlap handling when both free value and delay are present in the same case.
- Replaced generic sabotage-point language with case-shaped sabotage points tied to:
  - another free helpful move instead of paid transition
  - another round of proving value before talking about money
- Added phrasing constraints that explicitly tell diagnosis support not to collapse:
  - late paid boundary after free value
  - deferred money conversation after prove-more logic

## Before / After On Targeted Cases

### Case 1
- Name: `free_value_leakage_clear`
- Before live: `deferred_money_conversation`
- After live: `free_value_leakage`
- Before fallback: `free_value_leakage`
- After fallback: `free_value_leakage`
- Signal change: DNA now explicitly marks `бесплатная польза растягивается раньше платной границы`

### Case 2
- Name: `deferred_money_conversation_clear`
- Before live: `deferred_money_conversation`
- After live: `deferred_money_conversation`
- Before fallback: `deferred_money_conversation`
- After fallback: `deferred_money_conversation`
- Signal change: DNA now explicitly marks `денежный разговор переносится на потом под видом дополнительного доказательства ценности`

### Case 3
- Name: `overlap_value_giving_and_delay`
- Before live: `deferred_money_conversation`
- After live: `free_value_leakage`
- Before fallback: `free_value_leakage`
- After fallback: `free_value_leakage`
- Signal change: DNA now marks both overlap dimensions, but also adds the priority note that if delay happens after free value was already given, the primary failure is the paid boundary itself

### Case 4
- Name: `late_paid_boundary_after_free_help`
- Before live: `deferred_money_conversation`
- After live: `free_value_leakage`
- Before fallback: `underpricing_visibility_avoidance`
- After fallback: `underpricing_visibility_avoidance`
- Signal change: live meaning improved because DNA now emphasizes the late paid-boundary failure after unpaid value transfer

## Distinction Quality Result
- Live LLM improved on the highest-value weak pair.
- The strongest win is not broad intelligence growth, but cleaner diagnosis support for the `free_value_leakage` side of the boundary.
- `deferred_money_conversation` stayed stable and did not regress.
- Fallback stayed stable on the accepted clear cases.

## What Did Not Change
- Communication DNA still does not own the diagnosis.
- Communication DNA still does not route flow.
- Communication DNA still does not assign action.
- Product flow, module ownership, and state model were not rewritten.

## Remaining Weaknesses
- `late_paid_boundary_after_free_help` still shows fallback preferring `underpricing_visibility_avoidance`, so fallback adjacency on that edge is not fully solved.
- DNA is stronger on this pair, but it is still a support layer and depends on diagnosis quality to cash in the signal correctly.
- This pass did not widen into a broader DNA redesign.

## F-009 Output Signal
- Communication DNA now contributes materially better hidden-structure support on the confusable free-value / delayed-money boundary.
- The targeted live-vs-fallback comparison shows real improvement rather than prompt-only theory.

## Recommended Next Step
- Keep the next packet narrow.
- The best next frontier is either:
  - one more small calibration pass on the remaining `underpricing_visibility_avoidance` edge around late paid boundary cases
  - or a bounded `Communication DNA` uplift for another nearby confusion cluster only
