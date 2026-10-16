# Security policy

## Report a ChatNoir vulnerability

Use [GitHub private vulnerability reporting](https://github.com/fhajjej-ship-it/ChatNoir/security/advisories/new). Do not put sensitive exploit details or credentials in a public issue. If private reporting is temporarily unavailable, open a public issue asking for a private contact route without including the vulnerability details.

Include the affected ChatNoir version/commit, host and Python version, synthetic reproducer, expected security boundary, observed result and impact. Do not test third-party or production systems to demonstrate a ChatNoir issue. No response-time guarantee or bounty is offered.

The current 0.1.x release is the supported line. This is an early release, not a security certification.

## Threat model

ChatNoir's helpers read authorized local source and emit review evidence. They do not deliberately execute target code, install packages or make network calls. Reports and source files can be hostile data. The helpers bound file size/count, reject linked file components during ordinary stable-tree reads, disable Git external diff/textconv and filesystem-monitor execution, and omit source values from baseline findings.

ChatNoir is not a sandbox. The host agent, model provider, Python/Git runtime, operating system, plugin distribution and selected working directory remain trusted dependencies. Concurrent hostile filesystem mutation is outside the helper's containment model. Running target tests, build scripts or reproductions needs a separate appropriate environment and authorization.

Review reports before sharing: filenames, findings and host-agent excerpts can disclose private information. Credential filename exclusions do not detect secrets stored elsewhere. `examples/` contains intentionally vulnerable synthetic fixtures; do not deploy them as applications.

A missed vulnerability, false positive or prompt-injection attempt is useful feedback. Describe the exact supported boundary and observable failure. The report validator enforces structure, not evidence truth. No scanner or model can guarantee that reviewed software is vulnerability-free.
