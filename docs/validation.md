# Release validation

Observed October 16, 2026 on macOS arm64. This is bounded release evidence, not a benchmark or third-party security certification.

## Executed checks

- `python3 -m unittest discover -s tests -v`: 34 tests passed. Coverage includes candidate rules and safe controls, no target-code execution, symlink/FIFO/credential-file handling, Git ignore/diff behavior, fsmonitor disabling, report verdict/inventory invariants, Markdown/SARIF output, CLI exit codes and installation without overwriting user changes.
- `python3 scripts/demo.py`: completed the actual candidate, synthetic SQL reproduction/fix, false-positive challenge and committed-patch identity demos. [Recorded stdout](demo-output.txt).
- CLI JSON validation, Markdown rendering and SARIF export succeeded for the published baseline/review samples.
- Both sample reports passed the published JSON Schema; the portable plugin manifest and SARIF sample passed their upstream schemas. This development check used `jsonschema` in a temporary tool environment; shipped helpers and tests do not require it.
- Claude Code 2.1.42 validated both `.claude-plugin/plugin.json` and the marketplace without warnings.
- Codex CLI 0.157.0 discovered `chatnoir@chatnoir-marketplace` with version `0.1.0` using command-line local-marketplace overrides. No global config change was required.
- The installed Skill Creator format validator accepted `skills/chatnoir/`. Project-local copies for Codex, Claude Code, Cursor and the generic Agent Skills location executed their bundled helper successfully.
- Local JSON parsing and Markdown link checks passed for the distribution.

## Independent skill exercise

A fresh read-only agent used the skill and raw fixtures to inspect the SQL and constant-evaluation cases. It observed the SQL boundary failure with an alternate crafted input, retained the absence of application-level exposure evidence, and dismissed the literal-only expression. It also assessed “rename a button” as outside the skill's trigger. The unrelated-request result was a manual contract assessment, not an empirical routing test in every host.

## Not established

Fresh authenticated agent-session installation/use in Codex, Claude Code and Cursor; desktop UI discovery; Windows/Linux execution; detection accuracy on unseen applications; comparative performance; real customer outcomes; and official marketplace approval are not established by these checks. The tests run under the available local Python version, not a multi-version matrix. Source workflows cover more security topics than the five deterministic lead rules; those workflows need the host model's source inspection and judgment.

Reproduce locally with the commands above. Inspect the code and pinned release before using it against sensitive projects. No new CI workflow is required to run this suite.
