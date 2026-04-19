# F-007 Quality Review

## Scope
- Packet: `F-007 Real Case Quality Pass`
- Date: 2026-04-19
- Scenario scope: money/income only
- Runtime basis: accepted Russian runnable slice from `F-006`
- Environment note: no `OPENAI_API_KEY` was available during this pass, so the review used the local runnable baseline, strengthened fallback generation, and tightened LLM prompts/contracts for the same artifact boundaries.

## Cases Tested

### Case 1
- Name: `Фрилансер боится поднять цену`
- Core signal: fear of naming price directly, bonus-padding, offer softening
- Expected leading mechanism: `underpricing_visibility_avoidance`
- Quality result: diagnosis and action now stay centered on direct price naming instead of generic courage language

### Case 2
- Name: `Перегруженный специалист`
- Core signal: buying income through overwork and strain
- Expected leading mechanism: `money_through_strain`
- Quality result: diagnosis now separates overload from pricing fear and points toward a clean money move rather than more effort

### Case 3
- Name: `Эксперт с бесплатными консультациями`
- Core signal: too much free value before naming paid format
- Expected leading mechanism: `free_value_leakage`
- Quality result: restructuring and action now anchor on earlier paid-boundary naming

### Case 4
- Name: `Руководитель не просит повышение`
- Core signal: delaying the money conversation under the cover of proving value longer
- Expected leading mechanism: `deferred_money_conversation`
- Quality result: action now points to one initiated compensation conversation instead of vague preparation

### Case 5
- Name: `Предприниматель держится за маленький потолок`
- Core signal: staying in controllable smallness despite visible expansion opportunities
- Expected leading mechanism: `safety_in_smallness`
- Quality result: action routing was corrected so the output explicitly targets one bounded expansion step

### Case 6
- Name: `Специалист боится продаж`
- Core signal: endless preparation instead of one direct offer
- Expected leading mechanism: `sales_avoidance_preparation_loop`
- Quality result: action remains constrained to one direct offer without turning into a prep plan

### Case 7
- Name: `Эксперт путает ценность и тяжесть`
- Core signal: underpricing when work feels easy
- Expected leading mechanism: `value_discount_when_easy`
- Quality result: diagnosis now keeps value-versus-effort meaning intact and action points to pricing through result

### Case 8
- Name: `Страх отказа после одного нет`
- Core signal: collapsing price after the first rejection
- Expected leading mechanism: `rejection_collapse_pricing`
- Quality result: action now targets one non-collapse follow-up step rather than generic resilience phrasing

## Weak Patterns Found
- The previous fallback diagnosis logic collapsed too many cases into a small number of generic patterns.
- `safety_in_smallness` cases could be diagnosed correctly but still receive an overly generic action.
- Action quality needed stronger rejection of vague introspective phrasing such as `осознай`, `подумай`, `проанализируй`.
- Multi-action guardrails needed to be strict without falsely rejecting normal Russian phrasing that contains neutral `или`.
- Some older prompts allowed drift toward broad self-worth or motivational wording instead of concrete money-pattern restructuring.

## Improvements Made
- Expanded fallback mechanism detection from a coarse branch heuristic into a scored mechanism classifier across eight accepted money-pattern types.
- Tightened mechanism-specific diagnosis wording so each artifact stays closer to the tested real-case pattern.
- Tightened restructuring wording so the new cycle stays coupled to the diagnosed money mechanism instead of drifting into generic support language.
- Tightened action generation so each action is:
  - singular
  - externally testable
  - tied to one money move
  - resistant to vague introspection drift
- Corrected `safety_in_smallness` action routing so expansion cases produce expansion-specific actions.
- Refined action guardrails so true multi-action alternatives are rejected while legitimate explanatory phrasing is allowed.
- Kept deterministic fallback authority intact when generated outputs violate accepted contracts.

## Tests Added Or Strengthened
- Added a real-case harness covering 8 Russian money/income cases and asserting:
  - expected leading mechanism
  - expected action focus
- Added a test that rejects vague action outputs and verifies fallback replacement remains concrete.
- Re-ran the full accepted test suite after changes: `12/12` tests passed.

## Remaining Weaknesses
- Live external LLM quality was not re-verified in this environment because no API key was available during execution.
- `Communication DNA` remains lighter than the diagnosis/restructuring layer and may still miss subtler hidden-structure cues.
- The current quality pass strengthens one-cycle meaning quality, but not cross-cycle memory quality yet.
- Prompt quality is stronger, but still not calibrated against a larger corpus of real Russian cases.

## F-007 Output Signal
- The accepted runnable slice now handles a broader and more realistic set of Russian money/income cases without changing the canonical flow.
- The strongest discovered weak points have direct regression coverage.
- The next packet can work from a more trustworthy real-case baseline instead of a mostly template-like fallback.
