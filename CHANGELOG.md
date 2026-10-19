# Changelog

## 0.2.3 — October 19, 2026

- Added a guided first-review skill path for authentication, data access or agent permissions, reusing existing source review, evidence, reports and fix verification.
- Added the read-only `first-review` helper for local setup checks, included-file identity and a scoped agent handoff. Setup success does not claim a vulnerability review or host/model access.
- Linked the first-review path from the README and project-local installer. Existing v0.2.2 release downloads remain unchanged.

## 0.2.2 — October 17, 2026

- Packages the latest launch/compatibility documentation, fresh installed-skill results and seven-session real Codex evaluator with its sanitized actual-message evidence. Those provider-backed results were collected with 0.2.1; no new provider session is claimed for this packaging release.
- Fixes the evaluator’s hardcoded 0.2.1 verdict check: it now reads the selected installed helper’s version without executing it, and requires the reported and scanned versions to match. A regression covers 0.2.1/0.2.2 acceptance and mismatched-version rejection.
- Synchronizes all plugin manifests, helper version and download links at 0.2.2. Scanner rules and application authorization logic remain unchanged.
- Retains blocked Claude/fresh Cursor access, unexecuted adaptive same-agent rounds and bounded early-release claims. No continuous runtime shield, general swarm-defense guarantee or comparative accuracy claim.

## 0.2.1 — October 17, 2026

- Updated the README hook to “Protect what you build from agent attacks.” and aligned portable, Codex, Claude Code and Cursor plugin/marketplace descriptions with security review, attack-path analysis and fix verification.
- Published a refreshed download with synchronized plugin/helper versions and direct README ZIP/checksum links. Scanner rules and authorization behavior are unchanged from 0.2.0.
- Packaged the native CLI evaluation runners, synthetic coordinated approval-laundering example and measured evidence already merged since 0.2.0. The coordinated Codex/Cursor chain remains incomplete because Cursor hit its usage limit; offline controls and source review are kept distinct from successful mixed-host testing.
- The release retains explicit limits: no continuous runtime blocking, general swarm-defense guarantee or comparative-superiority claim. Packaging checks do not rerun provider model sessions.

## 0.2.0 — October 17, 2026

- Added CN006/CN007/CN008 Python heuristic leads for dynamic privileged prompt roles, JSON-to-action dispatch and message-supplied permission merges. These remain candidates requiring provenance, reachability and control validation.
- Added runnable synthetic prompt-injection, malicious-tool-output and agent-to-agent authority demos, fixed entrypoints, legitimate controls and an adversarial model-proposal check. No network, model calls or real credentials.
- Added agent-security review guidance, measured source-bound results and regressions for authorization, invalid proposals, import aliases, local bindings and documented detection limits.
- Indexed local statement/write lookups to avoid repeatedly scanning all preceding statements for unresolved prompt/action/permission names; added a structural work-bound regression.
- The demos use a scripted model and local action sink; no general live-model, swarm-protection or comparative-accuracy claim.

## 0.1.2 — October 16, 2026

- Fixed target-code execution through Git clean/process filters during inventory and scan dirty-state checks. Configured filters now leave dirty state unknown with a reason; submodule content is excluded from that check.
- Fixed Markdown output injection through crafted report text, backslashes, bare URLs and embedded newlines. Imported strings now remain literal text.
- Added regressions for clean/process filters, nested Git filters and imported report markup.
- Recorded a source-guided self-audit of the actual ChatNoir repository, with before/after runtime evidence and explicit coverage limits.

## 0.1.1 — October 16, 2026

- Fixed a missed SQL-injection lead when a constructed query is assigned to a local variable before execution; kept reassignment and function scope controls.
- Added an HTTP application with runnable SQL-injection, cross-user invoice and file-traversal attacks, plus fixed variants and legitimate controls.
- Added loopback HTTP boundary tests and a probe that ignores environment proxies.
- Closed SQLite connections explicitly in the original SQL demo.
- Recorded native Codex/Cursor detection, Codex remediation and independent HTTP verification, along with the Cursor remediation refusal and Claude authentication limit.
- Clarified that denied commands and provider refusals remain incomplete checks rather than successful verification.

## 0.1.0 — October 16, 2026

Initial public release:

- One portable security-review skill covering 15 workflows.
- Agent Plugins 1.0, Codex, Claude Code and Cursor manifests, plus repository marketplaces.
- Project-local installation for Codex, Claude Code, Cursor and Agent Skills hosts.
- Standard-library file inventory, five candidate rule families and exact committed-diff identity.
- Validated JSON reports, Markdown rendering and SARIF 2.1.0 export.
- Synthetic SQL-injection/fix, false-positive and patch-identity demonstrations.
- Black-cat identity and documented compatibility, privacy and detection limits.
