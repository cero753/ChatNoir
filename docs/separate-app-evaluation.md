# Separate real-app evaluation

Observed October 16, 2026 with ChatNoir 0.1.2 in the current Codex desktop chat. This assessment used a separate, publicly distributed TypeScript/Next.js application cloned into a disposable directory. It was neither ChatNoir itself nor the bundled vulnerable examples. The reviewed application's tracked source was left unchanged.

The target identity, source locations and full report are retained locally pending maintainer review of an unfixed finding. This public summary deliberately cannot serve as a fully reproducible public benchmark. It records the observed outcomes without disclosing the affected application or a target-specific attack recipe.

| Stage | Actual result |
|---|---|
| Installed baseline helper | 115 included files, 3 skips, **0 candidates**. JS/TS checks are lexical dynamic-evaluation matching only. |
| ChatNoir-guided source review | **1 confirmed low-severity code-level finding**, 5 dismissed candidates. This finding came from the agent workflow, not a baseline rule. |
| Bounded local validation | Invoked the application's actual request route/helper with local `Request` streams. One code-level finding was reproduced alongside a passing legitimate control. Target-specific behavior and inputs remain in the local report. |
| Existing app controls | **18 selected tests passed**, covering management authorization, origin/version checks, uploads and admission controls. Some database paths use mocks; no live database result is claimed. |
| ChatNoir report pipeline | The full local report passed validation, Markdown rendering and SARIF export. |
| ChatNoir implementation changes | No new implementation defect surfaced; no runtime patch was made. |

The public result ledger is [separate-app-results.json](e2e/separate-app-results.json). The distinction between a reproduced code-level weakness and practical deployment impact matters: upstream protections were not verified, no resource-exhaustion attack was attempted, and no production endpoint was contacted. This was an in-process route test, not a complete deployed-HTTP test.

The local run used a clean environment without production credentials or paid inference. Selected dependency versions matched the application's public lockfile; existing installed packages were reused rather than installed afresh. Network calls were disabled in the request-stream probe. Only local synthetic inputs and disposable records were used in the control tests.

This is a bounded, source-guided owner assessment, not an independent audit, blind accuracy test or evidence that every vulnerability was found. Zero baseline candidates did not close the review. Documented behavior and working controls were used to challenge potential false positives before reporting a finding.
