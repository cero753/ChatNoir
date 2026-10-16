# Contributing to ChatNoir

Bring a reproducible case, a useful negative control, or a clearer security boundary. Small, evidence-backed contributions are welcome.

For a bug or detector improvement, describe the supported language/runtime, exact affected behavior, minimal synthetic source and expected candidate disposition. Do not attach real credentials, customer code or an unreported third-party exploit to a public issue. Use [private vulnerability reporting](SECURITY.md) for ChatNoir vulnerabilities.

For a workflow change, explain which agent decision improves and which action boundaries remain. Keep `SKILL.md` small; route mode-specific guidance through references. Do not add vendor-only services to the portable core. No superiority claims or detection percentages without reproducible comparative evidence.

Before proposing a change:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/demo.py
```

Add focused tests when changing detector behavior, report contracts, file/Git handling or installation. Preserve the deliberately vulnerable examples and their labels. Keep runtime and network requirements explicit. Use existing trusted tooling if available; do not add dependencies for formatting alone.

Submit a focused pull request with the problem, resulting behavior and checks actually run. Contributions are under the repository's MIT license; include only work you have the right to contribute.
