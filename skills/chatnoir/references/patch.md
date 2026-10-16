# Diff review and patch risk

Resolve the actual base and head commits. `scripts/chatnoir.py diff` returns their full IDs, the patch digest, additions/modifications/deletions and an explicit committed-only scope. It does not review the patch. Inspect the diff with external diff/textconv disabled, deleted files at base, current implementations at head, and directly affected callers and contracts. Do not substitute HEAD for a dirty working-tree request. For uncommitted edits, retain the exact supplied patch and hash it; include staged, unstaged, untracked or binary changes only if actually captured. State omissions.

A changed helper can alter unchanged callers. Follow that concrete effect without turning a diff review into an unrelated repository sweep. Re-resolve moving refs before finalizing; if identity changed, report drift and bind a new comparison rather than combining evidence.

For an explicit patch-risk assessment, keep these dimensions separate:

| Dimension | Question |
|---|---|
| Impact | What breaks, and who or what is affected if the patch is wrong? |
| Likelihood | What source evidence makes regression plausible or unlikely? |
| Protection | Which relevant assertions/checks ran at the exact head? |
| Recovery | Can the change be reverted, including persisted state and migrations? |
| Confidence | Which decisive facts are established or unknown? |

Do not lower impact because tests pass. For each material changed boundary identify a concrete failure example and a legitimate case. Assess compatibility, trust/authority transitions, concurrency, persistent state and rollout only where the patch affects them.

Recommend `merge`, `revise`, `block`, `no_op` or `hold_for_evidence`. `merge` requires no known material defect or decision-critical unknown; `hold_for_evidence` names the smallest evidence that could change the decision. Explain the risk of leaving the current implementation separately. Recommendations never authorize a merge or replace required repository checks. ChatNoir does not automatically merge patches.
