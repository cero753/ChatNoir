# The 15 workflows

The agent performs these workflows through the installed skill. The CLI supplies evidence helpers; it does not automate all 15 workflows. Load the main `skills/chatnoir/SKILL.md` entrypoint and only the reference for the requested job.

| Workflow | Implementation | Result |
|---|---|---|
| 1. Assess patch risk | `references/patch.md` + committed-diff identity helper | Separate impact, regression likelihood, protection, recovery and confidence; advisory recommendation |
| 2. Attack-path analysis | `references/evidence.md` | Supported attacker-to-consequence chain with counterevidence |
| 3. Deep security review | `references/review.md` | Bounded additional review; sequential fallback when delegation is unavailable |
| 4. Define security policy | `references/policy.md` | Requested scoped policy draft/edit with owner decisions explicit |
| 5. Finding discovery | `references/review.md` + optional baseline leads | Distinct candidate locations and explicit coverage |
| 6. Fix a finding | `references/remediation.md` | Requested minimal source change plus focused proof |
| 7. Propose hardening | `references/hardening.md` | Evidence-backed structural options or a local-fix recommendation |
| 8. Security diff scan | `references/patch.md` + `references/review.md` | Review of changed behavior and affected callers, including deletions |
| 9. Repository/scoped scan | `references/review.md` | Declared scope, findings and unresolved surfaces |
| 10. Threat model | `references/policy.md` | Assets, actors, input control, boundaries and invariants |
| 11. Track findings | `references/disclosure.md` | Local drafts/ledger; authorized connector writeback when supplied |
| 12. Triage findings | `references/evidence.md` | One static verdict per input, with proof gaps retained |
| 13. Validate findings | `references/evidence.md` | Static or actual runtime evidence, labeled accurately |
| 14. Verify a fix | `references/remediation.md` | Fixed, still vulnerable, or inconclusive against the original path |
| 15. Vulnerability writeup | `references/disclosure.md` | Portable, source-backed report with reproduction limits |

Reference paths above are relative to `skills/chatnoir/`. Reports follow `references/report.md`; the repository also ships a JSON Schema under `schemas/`.

## Implementation choices

One router skill keeps installation small and works on hosts without custom agents, lifecycle hooks or MCP servers. The workflows do not call proprietary security services, require a hosted workbench, or assume one model. Deep review scales to host capabilities and the user's budget. External issue tracking uses the user's available connector or CLI only when requested.

## What is demonstrated

The public demos exercise a Python SQL-injection candidate, runtime reproduction against synthetic SQLite data, a parameter-binding fix, a literal-input false-positive challenge and committed-diff identity. The [agent-security demos](../examples/agent-attacks/README.md) add three narrow Python source patterns and actual synthetic prompt/tool/peer-message boundary failures, fixed controls and an adversarial model proposal. The model is scripted; no real LLM, distributed swarm or continuous runtime defense is evaluated. These demos do not establish broad vulnerability recall, precision, real-world adoption or superiority over another security product. Authentication, tenant isolation, memory safety and architecture hardening remain agent-review workflows, not benchmarked automated detectors.
