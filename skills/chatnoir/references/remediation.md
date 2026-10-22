# Fix and verify

## Fix a requested finding

Confirm the current state first. Trace the original input and control into the real operation, inspect direct callers and existing error conventions, and identify a focused legitimate behavior check. If the claim is disproved, report no change with evidence. If it remains unproven, do not hide that by making a speculative patch.

Place the remedy at the narrowest shared enforcement boundary that closes supported vulnerable paths. Account for relevant alternative representations, callers and state transitions; do not add unrelated hardening. Preserve API behavior, error semantics and existing work. Prefer existing libraries and patterns over a new dependency.

When authorized, run the original trigger and legitimate control before and after the fix. Add a focused regression test that observes the security boundary. Use a disposable copy when the target should remain read-only. Run affected required checks, and investigate failures rather than weakening assertions to pass. State unexecuted checks plainly.

Deliver the actual diff, evidence that the original boundary is closed, legitimate behavior retained, tests run and residual gaps. Fix authority does not include commit, push, merge, deploy or issue writeback.

For a retained review, incorporate those results into the same current report
using the existing finding IDs, dated evidence and refreshed target identity.
Keep unrelated unresolved findings and incident gaps; a verified code fix does
not settle them. Present one current report rather than an additional fix report.

If a host or provider blocks a requested step, preserve the unresolved result and report the blocked action and stated reason. Do not turn a refusal or tool-permission failure into evidence that the code is safe or the fix is verified.

## Verify without changing code

Preserve one result per supplied finding and do not edit source. Re-establish the original trigger and legitimate behavior against current code; follow moved implementations and equivalent supported paths. A missing line, closed ticket, passing unrelated suite, or absent baseline pattern does not prove remediation.

Return `fixed`, `still_vulnerable` or `inconclusive` with evidence, revision and validation method. `fixed` needs proof that the original vulnerable path is closed and legitimate behavior remains available. If runtime evidence is unavailable, state whether static analysis settles both properties or name the remaining proof gap. Never describe a static-only verdict as runtime verification.
