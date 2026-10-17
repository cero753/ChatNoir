# Changelog

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
