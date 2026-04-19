# F-010 Late Paid Boundary Review

## Scope
- Packet: `F-010 Late Paid Boundary Adjacency Pass`
- Date: 2026-04-19
- Target edge only:
  - `free_value_leakage`
  - `underpricing_visibility_avoidance`
- Focus question:
  - when late or softened price naming is a consequence of already leaked free value
  - versus when the primary failure is direct price avoidance without a real free-value leakage phase

## Exact Edge Targeted
- `late paid boundary after free help`
- `free help first, then blurred or softened price naming`
- `pure underpricing without meaningful free-value leakage`

## DNA Support Logic Changed
- Added a specific DNA cue for:
  - `после уже отданной бесплатно ценности цена смягчается слишком поздно вместо прямой платной границы`
- Added a specific DNA cue for:
  - `первичный сбой находится в прямом назывании цены, а не в утечке ценности в бесплатность`
- Added negation-aware free-value detection so phrases like `бесплатную ценность заранее не отдаю` do not falsely activate the free-value branch.
- Preserved the narrower `F-009` rule:
  - if delay happens after already leaked free value, DNA should still pull toward `free_value_leakage`

## Diagnosis Prompt Change
- Yes, but narrowly.
- The diagnosis prompt now makes the late-paid-boundary adjacency explicit:
  - if free value was already given and the later price naming is softened or blurred, prefer `free_value_leakage`
  - if there was no real unpaid-value phase and the primary failure is not naming price directly, prefer `underpricing_visibility_avoidance`
- Ownership did not change:
  - DNA remains support only
  - diagnosis remains diagnosis-owned

## Cases Re-Tested
1. `late_paid_boundary_after_free_help`
2. `free_help_then_soft_price`
3. `pure_underpricing_without_leakage`
4. `free_value_leakage_without_price_fear_center`
5. `free_value_leakage_clear_regression`
6. `underpricing_clear_regression`

## Before / After

### Case 1
- Name: `late_paid_boundary_after_free_help`
- Expected: `free_value_leakage`
- Before live: `free_value_leakage`
- After live: `free_value_leakage`
- Before fallback: `underpricing_visibility_avoidance`
- After fallback: `free_value_leakage`
- Result: primary targeted fallback confusion was fixed

### Case 2
- Name: `free_help_then_soft_price`
- Expected: `free_value_leakage`
- Before live: `free_value_leakage`
- After live: `free_value_leakage`
- Before fallback: `free_value_leakage`
- After fallback: `free_value_leakage`
- Result: stayed stable, no regression

### Case 3
- Name: `pure_underpricing_without_leakage`
- Expected: `underpricing_visibility_avoidance`
- Before live: `underpricing_visibility_avoidance`
- After live: `underpricing_visibility_avoidance`
- Before fallback: `underpricing_visibility_avoidance`
- After fallback: `underpricing_visibility_avoidance`
- Result: stayed stable, and DNA no longer falsely injects free-value leakage support into the case

### Case 4
- Name: `free_value_leakage_without_price_fear_center`
- Expected: `free_value_leakage`
- Before live: `free_value_leakage`
- After live: `free_value_leakage`
- Before fallback: `free_value_leakage`
- After fallback: `free_value_leakage`
- Result: stayed stable, no regression

### Case 5
- Name: `free_value_leakage_clear_regression`
- Expected: `free_value_leakage`
- Before live: `free_value_leakage`
- After live: `free_value_leakage`
- Before fallback: `free_value_leakage`
- After fallback: `free_value_leakage`
- Result: accepted clear case preserved

### Case 6
- Name: `underpricing_clear_regression`
- Expected: `underpricing_visibility_avoidance`
- Before live: `underpricing_visibility_avoidance`
- After live: `underpricing_visibility_avoidance`
- Before fallback: `underpricing_visibility_avoidance`
- After fallback: `underpricing_visibility_avoidance`
- Result: accepted clear case preserved

## What Improved
- The packet fixed the intended fallback-side confusion on the late-paid-boundary edge.
- The support layer now distinguishes:
  - price avoidance after already leaked free value
  - price avoidance without a real leakage phase
- The adjustment stayed narrow and did not widen into a broader mechanism redesign.

## What Still Remains Weak
- This pass only closes one adjacency edge; it does not claim a broad DNA upgrade.
- Live and fallback now agree better on this edge, but wider mechanism-cluster calibration is still a separate concern.
- The system still depends on deterministic validation and fallback discipline overall.

## F-010 Output Signal
- The targeted late-paid-boundary adjacency is materially cleaner now.
- The main measurable win is fallback behavior, not a general intelligence claim.

## Recommended Next Step
- Keep the next packet narrow.
- Best next step after `F-010`:
  - pause for manager review first
  - then, only if needed, open a new bounded packet on one different adjacency cluster rather than continuing to widen this one
