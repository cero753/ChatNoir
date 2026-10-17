# Launch readiness

Reviewed October 17, 2026. **Ready for an early public release as an evidence-first security review skill and local helper.** The verified scope supports that positioning, with explicit host-access and coverage limits. This is an owner-run launch review, not independent certification or proof of customer demand.

## Verified scope

| Surface | Evidence |
|---|---|
| Codex | Installed v0.2.1 source reviews reproduced the known HTTP and coordinated flaws. [Installed HTTP results](installed-0.2.1-e2e.md), [coordinated review](coordinated-agent-security.md#fresh-installed-v021-follow-up) |
| Multiple real Codex agents | Seven distinct sessions authored and handed off actual messages. ChatNoir found the missing root authorization; the fixed app denied those messages and preserved summaries. The coordinator resisted the attack. [Exact messages and results](codex-coordinated-attack.md) |
| Cursor | Earlier CLI detection and IDE project-skill review/remediation passed. Native desktop installation and v0.2.1 descriptions were later checked separately. The latest fresh model request hit its usage limit before inference. [Historical IDE results](desktop-e2e.md), [fresh access limit](installed-0.2.1-e2e.md) |
| Claude Code | Manifest validation and native discovery passed. Model requests failed authentication; no successful detection/remediation run is claimed. [Harness evidence](harness-e2e.md) |
| Local implementation | 80 repository tests and the included demos passed. Coverage includes scanner/report/file/Git handling, installation, synthetic app fixes and native-evaluator verdicts. [Validation record](validation.md) |
| Distribution | The downloaded v0.2.1 ZIP matched its checksum and all 98 tagged files. The packaged helper and four demos passed; project-local installs for Codex, Cursor, Claude and generic Agent Skills executed helper version 0.2.1. Repository Markdown file links passed. |

## Corrections in this review

- Updated the security policy's obsolete supported line from 0.1.x to 0.2.x.
- Reconciled Cursor installation wording with the later native installation checks while retaining the fresh model-access blocker.
- Made the unexecuted adaptive test and current launch limits visible from the README.

No new scanner or skill runtime defect was established. The plugin remains v0.2.1. This documentation update does not alter the existing release assets or rewrite history.

## Limits to retain publicly

- ChatNoir reviews code and verifies specific fixes; continuous runtime blocking, general swarm protection, comparative superiority and a fixed detection rate are unproven.
- The eight deterministic rule families emit candidates. The coordinated authorization flaw required source-guided review despite zero candidates.
- Adaptive attacks in which the same live agents revise messages from failure feedback **have not run**. The owner reported a content-access restriction in the interface; no successful adaptive execution or local CLI refusal was observed, and no workaround was attempted.
- Only the documented environments and flows are verified. Provider authentication, quota and content controls can prevent a review even when installation succeeds.
- Historical public-reference cleanup has no verified closure in this review. Current docs are anonymized; no claim that all historical objects have been removed is made. Existing history is preserved.

The v0.2.1 download is an immutable tagged snapshot. Newer case studies and the all-Codex evaluator were added on `main` afterward; clone the repository to use those additions. They are not silently added to the old ZIP. [Release download](https://github.com/fhajjej-ship-it/ChatNoir/releases/tag/v0.2.1).
