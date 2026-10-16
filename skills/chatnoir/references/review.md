# Repository, scoped, diff and deep review

## Establish coverage

Resolve the requested directory and scope first. Record the current revision and dirty state; use the helper inventory when useful. A working-tree review concerns current file bytes, not just HEAD. Identify entrypoints, supported languages, frameworks, deployment assumptions, dependencies and security policies. Do not dump whole environment files or credentials.

Create a short coverage ledger of relevant surfaces: authentication, per-resource authorization and tenant separation; input parsing and serialization; database/query construction; filesystem/archive operations; outgoing requests and redirects; command/code execution; secrets and cryptography; browser rendering and sessions; jobs, webhooks and payment state; build/dependency boundaries. Mark each surface reviewed, not applicable, or deferred with a reason. This is a navigation aid, not a list of presumed findings.

The local baseline can identify leads in Python and dynamic-evaluation patterns in JS/TS. Review source in other languages directly with the agent's tools and existing project tooling. Do not call a language supported by the deterministic scanner merely because the agent can read it.

## Discover and challenge

Start from externally influenced values and sensitive operations. Follow entrypoint → parsing/transformation → enforcement → final operation. Inspect authentication separately from ownership checks. Recheck authority after redirects, canonicalization, aliases, deferred jobs, retries and state changes when relevant. Inspect failure paths, not just successful requests.

Use the code's actual contract. An unsafe-looking call is a candidate until lower-trust influence, realistic reachability, a broken control and security impact are established. Find the strongest reason the claim might be false, and trace that control too. Tests and documentation show intent; assertions and implementation establish what they actually protect.

Keep separate independently reachable instances, while grouping shared root causes in prose if helpful. Never silently drop a candidate: close it as confirmed, dismissed with counterevidence, or needs_review with a specific proof gap. Continue with [evidence](evidence.md).

## Deep review

Deep means an additional deliberate pass over the **same** scope, not an unbounded scan. State a time budget and which independent perspective would help: for example attacker entrypoints versus sensitive sinks, or authorization logic versus lifecycle/race behavior. Do not impose a model, vendor, worker count or hidden spending requirement.

If the host supports delegation and the user or host permits it, separate non-overlapping review tasks and have one owner reconcile evidence. Otherwise do the second pass sequentially and label it as such. Do not describe sequential self-review as an independent external audit. Deduplicate by affected operation/root control, preserve conflicting evidence, and retain unfinished coverage. Stop at the agreed budget with explicit gaps.

## Finish

Report what was inspected, the evidence supporting findings, candidates not settled, skipped files and untested environments. `coverage.complete` concerns completion of the **declared review scope**, never a guarantee that all vulnerabilities were found. It must remain false while relevant work is deferred. Model-based reviews depend on the host model, context window, tools and reviewer judgment; no fixed detection rate is claimed.
