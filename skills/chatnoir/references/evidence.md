# Validation, attack paths and triage

For each claim, retain the input identifier and order. A claim from a tool, advisory or ticket is not automatically true. Read the exact affected component and version when available; note mismatches rather than changing revisions or installing dependencies silently.

## Evidence record

Answer these questions with file/line references and clear unknowns:

1. Who can influence the input, with what initial privileges?
2. Which supported entrypoint accepts it, and how does it reach the sensitive operation?
3. What control should stop it, and why does that control fail on this path?
4. What separate asset, owner, privilege or availability boundary is crossed?
5. What is the strongest counterexample or legitimate control, and what does it establish?

Separate observed source, supplied claims, runtime observations, inference and unknowns. Do not assert broad affected versions from a current checkout. Dependency version/advisory analysis requires an actual resolved version and authoritative advisory evidence, with dates when retrieved.

## Validate

Prefer a minimal reproduction through the original interface when authorized and feasible. Use synthetic data in a disposable target, with the original trigger and a legitimate control. Record exact command, revision, outcome and limits; inspect project test commands before execution. A local test server is not permission to contact an external service. Crashes or resource-exhaustion tests require effective containment.

If execution is unavailable or disproportionate, a complete static trace can establish a vulnerability. Label the method `static`; never call it reproduced. Missing services, failed builds and absent tests do not disprove a claim. Keep a material reachability, trust or control gap as `needs_review`.

## Attack path and severity

Write the actual chain in plain language: attacker position → controlled value → reachable operation → failed enforcement → demonstrated consequence. Use only supported steps. Consider required privileges, default versus optional configuration, victim interaction, blast radius and recoverability. Set severity to `unknown` if decisive facts are unavailable. State impact separately from confidence; a serious issue with weak evidence is not a confirmed critical vulnerability.

## Triage existing findings

Triage is static and read-only unless the user also requests validation or fixes. Retrieve only selected reports/tickets through authorized tools. Preserve every input, including duplicates, and its source ID. Return one verdict per item:

- `confirmed`: a complete supported path crosses a security boundary.
- `dismissed`: positive evidence defeats the claim; include that evidence.
- `needs_review`: specify the fact needed to settle it.

Rank confirmed findings and unresolved candidates separately by realistic exploitability and impact. Do not create or update source tickets while triaging. Give a fix handoff only after establishing the boundary and legitimate behavior to preserve.
