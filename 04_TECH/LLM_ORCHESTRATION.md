# LLM Orchestration

## Responsibility Split

### Deterministic Code
- Owns flow order
- Owns state transitions
- Owns persistence
- Owns packet discipline
- Owns validation and schema checks

### Communication DNA Layer
- Interprets hidden structure in user language
- Surfaces resistance and prohibition signals
- Supports mechanism diagnosis

### LLM Layer
- Converts diagnosis into a user-ready explanation
- Produces admissible new belief phrasing
- Generates one bounded micro-action
- Interprets check-in response inside the fixed schema

## Orchestration Rule
- LLM output must fit deterministic schemas.
- LLM is not allowed to invent a new stage in the flow.
- DNA output informs diagnosis but does not bypass code-owned transitions.

## MVP Processing Order
1. Capture intake
2. Run DNA interpretation
3. Build leading mechanism hypothesis
4. Generate old cycle and new cycle
5. Generate one action
6. Process check-in
7. Write progress snapshot
