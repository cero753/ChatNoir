# Release validation

Observed October 16, 2026 on macOS arm64. This is bounded release evidence, not a benchmark or third-party security certification.

## Executed checks

- `python3 -m unittest discover -s tests -v`: 38 tests passed. Coverage includes candidate rules and safe controls, no scanner execution of target code, symlink/FIFO/credential-file handling, Git ignore/diff behavior, fsmonitor disabling, report verdict/inventory invariants, Markdown/SARIF output, CLI exit codes and installation without overwriting user changes. New checks reproduce the SQL-variable miss, verify assignment scope/reassignment, and exercise the vulnerable/fixed HTTP routes.
- `python3 scripts/demo.py`: completed the actual candidate, synthetic SQL reproduction/fix, false-positive challenge and committed-patch identity demos. [Recorded stdout](demo-output.txt).
- CLI JSON validation, Markdown rendering and SARIF export succeeded for the published baseline/review samples.
- Both sample reports passed the published JSON Schema; the portable plugin manifest and SARIF sample passed their upstream schemas. This development check used `jsonschema` in a temporary tool environment; shipped helpers and tests do not require it.
- Claude Code 2.1.42 validated both `.claude-plugin/plugin.json` and the marketplace without warnings.
- Codex CLI 0.157.0 discovered `chatnoir@chatnoir-marketplace` with version `0.1.0` using command-line local-marketplace overrides. No global config change was required.
- The installed Skill Creator format validator accepted `skills/chatnoir/`. Project-local copies for Codex, Claude Code, Cursor and the generic Agent Skills location executed their bundled helper successfully.
- Local JSON parsing and Markdown link checks passed for the distribution.

## Native provider sessions

The [end-to-end report](harness-e2e.md) and [normalized evidence](e2e/results.json) record actual CLI model sessions. Codex and Cursor each loaded ChatNoir natively, found/reproduced the three known HTTP-fixture vulnerabilities, and dismissed the constant-expression negative control. Codex then generated and verified a patch; an independent loopback HTTP probe passed all 8 checks against that exact patched source. Cursor's provider blocked remediation. Claude's model request was blocked by authentication, although its native plugin was discovered. These are distinct outcomes, not three complete passes.

## Desktop and IDE sessions

The [desktop report](desktop-e2e.md) records a Cursor 3.24.12 IDE run through the native `/chatnoir` skill picker with the visible default model, Cursor Grok 4.6 Medium. It loaded the references/helper, reproduced all three flaws, dismissed constant `eval`, generated a patch and reported 13 passing in-memory WSGI checks. A separate evaluator HTTP probe passed all 8 checks against that exact patch. The current Codex desktop chat also used its natively available installed skill and verified a disposable patch with 8 HTTP checks; this owner chat had prior fixture knowledge. Codex self-UI automation was blocked, so no fresh install/picker screen is claimed. See [normalized desktop results](e2e/desktop-results.json). No ChatNoir code change was required by these tests.

## Independent skill exercise

A fresh read-only agent used the skill and raw fixtures to inspect the SQL and constant-evaluation cases. It observed the SQL boundary failure with an alternate crafted input, retained the absence of application-level exposure evidence, and dismissed the literal-only expression. It also assessed “rename a button” as outside the skill's trigger. The unrelated-request result was a manual contract assessment, not an empirical routing test in every host.

## Not established

Full Claude model-session behavior; remediation in the earlier Cursor CLI Auto session; fresh Codex desktop install/picker screens; Cursor IDE marketplace/plugin installation; Windows/Linux execution; detection accuracy on unseen applications; comparative performance; real customer outcomes; and official marketplace approval are not established by these checks. The tests run under the available local Python version, not a multi-version matrix. Source workflows cover more security topics than the five deterministic lead rules; those workflows need the host model's source inspection and judgment.

Reproduce locally with the commands above. Inspect the code and pinned release before using it against sensitive projects. No new CI workflow is required to run this suite.
