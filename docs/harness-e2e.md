# Native harness end-to-end tests

Observed October 16, 2026 on macOS arm64. Tests used actual provider-backed CLI sessions and the native ChatNoir plugin, not simulated assistant answers. The target was the [synthetic HTTP application](../examples/http-app/README.md). These are known local fixture cases, not unseen applications or a comparative accuracy benchmark.

## Method

Each harness received a separate temporary Git checkout containing a neutrally named application and its intended contracts. Expected vulnerability labels and the evaluator's HTTP probe were kept outside the target. The request named ChatNoir, required native skill loading, source review, candidate validation and false-positive handling, and confined work to the synthetic app and plugin resources.

The vulnerable app has three independently demonstrated boundary failures: category input changes SQL syntax, Alice can retrieve Bob's invoice, and a filename escapes the public download directory. `/health` uses a fixed expression with no caller influence and is a negative control. The evaluator's separate loopback HTTP probe reproduces the failures and checks the fixed app against the same attacks and five legitimate/authentication controls.

Review sessions were read-only. Authorized remediation sessions could edit only `app.py` in a disposable copy. No production targets, real user data, new purchases, API keys or live-system probing were used. Existing provider accounts supplied inference. Raw session traces remain local; public artifacts contain final outcomes and source patches, not private account details or reasoning traces.

## Results

| Harness | Native skill and source review | Detection / false positive | Remediation and verification |
|---|---|---|---|
| Codex CLI 0.157.0; `gpt-6-sol`, high reasoning | Loaded the installed `0.1.1` skill, review/evidence references and baseline helper from Codex's plugin cache | Confirmed all three flaws through in-memory calls to the actual app; dismissed constant `eval` | Produced a minimal patch and verified through WSGI calls. The evaluator independently tested the patched app over HTTP: all 8 checks passed. |
| Cursor CLI 2026.05.16-0338208; Auto | Loaded the native plugin skill and references, ran the baseline, read source and contracts | Confirmed all three flaws through actual in-memory calls; dismissed constant `eval`. A separate static review of the already-fixed control returned no confirmed findings and four evidence-backed dismissals. | Provider blocked the subsequent remediation request under its cyber-content restrictions before code edits. Automated remediation is not verified. |
| Claude Code 2.1.42 | Native initialization listed `chatnoir:chatnoir` and the plugin | The initial and follow-up model requests returned an invalid OAuth token error | Valid model access was unavailable for the follow-up test. Detection and remediation remain unverified. |

Codex initially rejected the user's default `gpt-6.1-sol`; the user explicitly approved `gpt-6-sol` with high reasoning for these tests. This is a test-runtime choice, not a model requirement imposed by ChatNoir.

The accepted [Codex patch](e2e/codex-fix.diff) is used as the public fixed fixture. Its independent HTTP results are available in the [normalized evidence](e2e/results.json).

Retained final reports: [Codex vulnerable-app review](e2e/codex-review.json), [Cursor vulnerable-app review](e2e/cursor-review.json), and [Cursor fixed-control review](e2e/cursor-control.json). The control report also passed ChatNoir's report validator. It is a source-only assessment; application runtime verification belongs to the separate HTTP probe.

## Failures found and handled

- The baseline missed SQL assembled in a local variable before execution. A failing regression reproduced that miss. CN004 now follows simple earlier assignments in the same statement block while respecting reassignment and function boundaries. Branches, closures and general taint analysis remain outside this rule's scope.
- Cursor plan mode denied Python helper/runtime commands. Static findings were kept separate from execution. The successful runtime review used normal agent mode with a project-local permission allowlist for the trusted synthetic fixture. The unavailable optional sandbox was not represented as working. No `--force`/`--yolo` bypass was used.
- Codex marketplace discovery alone was insufficient: the plugin had to be installed. An incorrectly quoted command-line plugin key in the test runner also prevented loading; correcting the test setup restored native skill discovery. Neither failure is counted as a successful review.
- Cursor's remediation provider refusal is retained as a blocked result. It was not retried through altered prompts or another model to evade the restriction. A separate static review of the already-fixed control is a different, safer test and does not count as Cursor-generated remediation.
- Claude initially returned a structured authentication error despite a zero process exit code and a cached “logged in” status. A follow-up review request on October 16 also returned HTTP 401 with `is_error: true`, used zero model tokens and left the fixture unchanged. Valid model access was unavailable, so review and remediation remain blocked. Native plugin discovery is established; a successful model session is not. CLI exit status alone is not a sufficient test verdict.

## Desktop follow-up

A subsequent [desktop/IDE test](desktop-e2e.md) verified Cursor's project skill picker, review and remediation using its visible default IDE model, Cursor Grok 4.6 Medium. It also exercised the installed skill in the current Codex desktop chat, with the self-UI automation limit stated explicitly. These are separate runs; the earlier CLI provider refusal and Claude access block remain recorded above.

## Reproduce

Install ChatNoir using the [host-specific instructions](compatibility.md), make a disposable copy of `examples/http-app/vulnerable`, and provide the intended contracts from its README. Ask the host to load ChatNoir natively, review the app read-only, and distinguish source evidence from runtime observations. Keep the probe outside the agent's target while reviewing.

After an authorized fix in the disposable copy, run:

```sh
python3 scripts/http_probe.py /path/to/disposable-app
```

For baseline/control checks that do not need a model account:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/http_probe.py examples/http-app/vulnerable
python3 scripts/http_probe.py examples/http-app/fixed
```

The vulnerable command intentionally exits 1. The fixed command must exit 0 with all checks true. Provider authentication, model availability and content restrictions are external dependencies; native manifests cannot override them.
