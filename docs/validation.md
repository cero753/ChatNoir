# Release validation

Observed October 16, 2026 on macOS arm64. This is bounded release evidence, not a benchmark or third-party security certification.

## Executed checks

- Version 0.1.1: `python3 -m unittest discover -s tests -v` passed 38 tests. Coverage includes candidate rules and safe controls, no scanner execution of target code, symlink/FIFO/credential-file handling, Git ignore/diff behavior, fsmonitor disabling, report verdict/inventory invariants, Markdown/SARIF output, CLI exit codes and installation without overwriting user changes. New checks reproduce the SQL-variable miss, verify assignment scope/reassignment, and exercise the vulnerable/fixed HTTP routes.
- `python3 scripts/demo.py`: completed the actual candidate, synthetic SQL reproduction/fix, false-positive challenge and committed-patch identity demos. [Recorded stdout](demo-output.txt).
- CLI JSON validation, Markdown rendering and SARIF export succeeded for the published baseline/review samples.
- Both sample reports passed the published JSON Schema; the portable plugin manifest and SARIF sample passed their upstream schemas. This development check used `jsonschema` in a temporary tool environment; shipped helpers and tests do not require it.
- Claude Code 2.1.42 validated both `.claude-plugin/plugin.json` and the marketplace without warnings.
- Codex CLI 0.157.0 discovered `chatnoir@chatnoir-marketplace` with version `0.1.0` using command-line local-marketplace overrides. No global config change was required.
- The installed Skill Creator format validator accepted `skills/chatnoir/`. Project-local copies for Codex, Claude Code, Cursor and the generic Agent Skills location executed their bundled helper successfully.
- Local JSON parsing and Markdown link checks passed for the distribution.

## Version 0.1.2 real-project audit

The [real-project self-audit](real-project-audit.md) reviewed ChatNoir's shipped helper, installer and report boundaries. Source review found and harmless local execution reproduced Git filter execution during dirty-state checks and imported Markdown injection. Both were fixed. The updated suite passed 42 tests; actual repository inventory/scan, report validation, Markdown/SARIF export, demos and manifest validation succeeded. The [structured verification](e2e/real-project-review.json) preserves source hashes, prerequisites, baseline dispositions and remaining gaps. This is an owner self-review, not a blind or external audit.

## Separate real application

A subsequent [separate-app evaluation](separate-app-evaluation.md) used a disposable clone of a real TypeScript/Next.js application. ChatNoir's installed baseline returned zero leads; its source-guided workflow confirmed one low-severity code-level finding and dismissed five candidates. Actual route/helper validation and 18 selected application control tests ran locally. The complete report passed validation, Markdown rendering and SARIF export. The target was Workshop Prep Agent: its shared JSON reader buffered an oversized request before checking the limit (low severity, CWE-400). The subsequently authorized fix added incremental decoding and early cancellation. All 24 focused app tests, typecheck and production webpack build passed; the exact fix commit deployed successfully and a read-only production config smoke returned HTTP 200. The case links the public patch and regression tests. Body cancellation was verified locally, not with oversized production requests. No new ChatNoir implementation defect or runtime patch resulted. This is distinct from the self-audit and demo fixtures.

## Another real application: Roadster Reference

The [Roadster Reference evaluation](roadster-evaluation.md) reviewed a separate Python-built static web app at pinned commit `d37ada4bd81cd8228c4865286e24964e7e25c8fc`. The baseline included 32 files with no file skips and returned zero candidates. Guided source review confirmed no vulnerabilities and dismissed four hypotheses. Nine existing tests, data/link validation, the 17-page static build and six local boundary controls passed. The structured local report validated and exported to Markdown/SARIF; target file hashes were unchanged. No new ChatNoir implementation defect or runtime patch resulted. Output-parser controls do not claim browser or production execution. See the [result ledger](e2e/roadster-results.json) for scope and remaining gaps.

## Backend, authentication and database

The [backend evaluation](backend-evaluation.md) used selected routes/middleware from an existing private app with service tokens, signed JWTs and real PostgreSQL. The baseline returned zero candidates across 23 included files, with two binary skips. All 18 local API integration checks passed: credential rejection and legitimate controls, JWT signature/expiry/role checks, bound SQL values, worker workspace consistency and unchanged synthetic records. Four hypotheses were dismissed; no vulnerability or new ChatNoir defect was confirmed. Full local report validation/export and unchanged target-byte checks passed. This used ASGI request integration and a minimal synthetic database schema; browser/provider sign-in, full startup, frontend customer authorization and production behavior remain untested. Private source and raw traces were not published. See the [aggregate ledger](e2e/backend-results.json).

## Native provider sessions

The [end-to-end report](harness-e2e.md) and [normalized evidence](e2e/results.json) record actual CLI model sessions. Codex and Cursor each loaded ChatNoir natively, found/reproduced the three known HTTP-fixture vulnerabilities, and dismissed the constant-expression negative control. Codex then generated and verified a patch; an independent loopback HTTP probe passed all 8 checks against that exact patched source. Cursor's provider blocked remediation. Claude's model request was blocked by authentication, although its native plugin was discovered. These are distinct outcomes, not three complete passes.

## Desktop and IDE sessions

The [desktop report](desktop-e2e.md) records a Cursor 3.24.12 IDE run through the native `/chatnoir` skill picker with the visible default model, Cursor Grok 4.6 Medium. It loaded the references/helper, reproduced all three flaws, dismissed constant `eval`, generated a patch and reported 13 passing in-memory WSGI checks. A separate evaluator HTTP probe passed all 8 checks against that exact patch. The current Codex desktop chat also used its natively available installed skill and verified a disposable patch with 8 HTTP checks; this owner chat had prior fixture knowledge. Codex self-UI automation was blocked, so no fresh install/picker screen is claimed. See [normalized desktop results](e2e/desktop-results.json). No ChatNoir code change was required by these tests.

## Independent skill exercise

A fresh read-only agent used the skill and raw fixtures to inspect the SQL and constant-evaluation cases. It observed the SQL boundary failure with an alternate crafted input, retained the absence of application-level exposure evidence, and dismissed the literal-only expression. It also assessed “rename a button” as outside the skill's trigger. The unrelated-request result was a manual contract assessment, not an empirical routing test in every host.

## Not established

Full Claude model-session behavior; remediation in the earlier Cursor CLI Auto session; fresh Codex desktop install/picker screens; Cursor IDE marketplace/plugin installation; Windows/Linux execution; detection accuracy on unseen applications; comparative performance; real customer outcomes; and official marketplace approval are not established by these checks. The tests run under the available local Python version, not a multi-version matrix. Source workflows cover more security topics than the five deterministic lead rules; those workflows need the host model's source inspection and judgment.

Reproduce locally with the commands above. Inspect the code and pinned release before using it against sensitive projects. No new CI workflow is required to run this suite.
