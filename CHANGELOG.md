# Changelog

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
