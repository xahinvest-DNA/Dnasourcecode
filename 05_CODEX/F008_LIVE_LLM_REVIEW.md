# F-008 Live LLM Review

## Scope
- Packet: `F-008 Live LLM Calibration Pass`
- Date: 2026-04-19
- Scenario scope: money/income only
- Comparison basis: accepted 8 Russian real-case set from `F-007`
- Runtime basis: live OpenAI-backed meaning generation with deterministic validation and fallback safety preserved

## Cases Tested Live
1. `Фрилансер боится поднять цену`
2. `Перегруженный специалист`
3. `Эксперт с бесплатными консультациями`
4. `Руководитель не просит повышение`
5. `Предприниматель держится за маленький потолок`
6. `Специалист боится продаж`
7. `Эксперт путает ценность и тяжесть`
8. `Страх отказа после одного нет`

## Initial Live Failure Modes Found
- `leading_mechanism_hypothesis` often came back as a descriptive sentence instead of a canonical mechanism label.
- `ActionOutput` often drifted into outcome-based completion criteria such as waiting for client response or income growth.
- Some actions drifted into research, investing, platform registration, or planning instead of one bounded money move.
- Some valid-looking outputs were still too terse to be reliable as a user-facing action contract.
- One probe round showed timeout sensitivity on longer live calls, so the default timeout needed more headroom.

## Calibration Changes Made
- Tightened the diagnosis prompt so `leading_mechanism_hypothesis` must use one canonical label only.
- Added explicit mapping hints inside the diagnosis prompt for:
  - `underpricing_visibility_avoidance`
  - `free_value_leakage`
  - `deferred_money_conversation`
  - `sales_avoidance_preparation_loop`
  - `value_discount_when_easy`
  - `rejection_collapse_pricing`
  - `safety_in_smallness`
- Tightened the action prompt so:
  - action must stay inside one money move
  - completion criterion must describe completion of the user's own step
  - action may not drift into investing, platform registration, studying options, or planning
  - short-horizon phrasing is preferred
- Tightened validation so:
  - diagnosis rejects non-canonical mechanism labels
  - action rejects multi-option and planning drift more aggressively
  - completion criterion rejects external-outcome phrasing
- Increased default LLM timeout from `30` to `60` seconds.

## Final Live-vs-Fallback Comparison

### Where Live LLM Was Stronger
- `Фрилансер боится поднять цену`
  - Live correctly converged to `underpricing_visibility_avoidance` after calibration and produced a direct price-naming action.
- `Предприниматель держится за маленький потолок`
  - Live produced a more concrete expansion action than the fallback, which stayed more generic.
- `Руководитель не просит повышение`
  - Live produced a reasonably direct compensation-request action with correct canonical mechanism.
- `Страх отказа после одного нет`
  - Live held the correct rejection-collapse pattern and produced a concrete price-hold/request step.

### Where Fallback Still Outperformed Live
- `Эксперт с бесплатными консультациями`
  - Live still collapsed the case into `deferred_money_conversation`, while fallback stayed closer to `free_value_leakage`.
- `Перегруженный специалист`
  - Live identified the mechanism correctly, but the final action contract remained too terse and would need fallback at runtime.
- `Специалист боится продаж`
  - Live identified `sales_avoidance_preparation_loop`, but the final action contract remained too terse and would need fallback at runtime.

### Mixed Cases
- `Эксперт путает ценность и тяжесть`
  - Live landed on the correct mechanism and produced a workable action, but the wording was still more generic than the best fallback phrasing.

## Final Reliability Signal
- After calibration, live LLM completed `6/8` cases with valid end-to-end artifacts inside deterministic contracts.
- The remaining `2/8` cases were safely rejected by validation and would fall back at runtime rather than breaking the cycle.
- Live LLM is now usable as the primary meaning layer only with deterministic validation and fallback enabled.
- Live LLM is not trustworthy enough yet as an unguarded standalone source of product meaning.

## Regression Coverage Added
- non-canonical diagnosis labels now trigger fallback
- outcome-based completion criteria now trigger fallback
- research / investing drift in actions now triggers fallback
- overly terse completion criteria now trigger fallback

## Recommended Next Step
- Keep live LLM as the primary generator behind deterministic validation and fallback.
- Open the next bounded packet only if it stays narrow:
  - either `Communication DNA` quality uplift
  - or a second live calibration pass focused only on the still-weak misclassification between `free_value_leakage` and `deferred_money_conversation`
