# Real app: Workshop Prep Agent

Observed October 16, 2026 with ChatNoir 0.1.2 in Codex desktop. This assessment used a disposable clone of [Workshop Prep Agent](https://github.com/fhajjej-ship-it/workshop-prep-agent), a separate TypeScript/Next.js application. It was neither ChatNoir itself nor a bundled vulnerable fixture.

## Finding and fix

At [reviewed commit `83daa0c`](https://github.com/fhajjej-ship-it/workshop-prep-agent/tree/83daa0c5befb6ae6c7a2184fdb9aa6438d7da0a6), `lib/http.ts:20` called `request.text()` before checking the configured character limit. The actual create route consumed an entire 1,048,576-byte ASCII request before returning 413 for its 250,000-character limit, without cancelling the stream. This confirmed a **low-severity code-level buffering weakness, CWE-400**. Practical availability impact depends on upstream protections; production denial of service was not established.

[Fix commit `6fbd0bd`](https://github.com/fhajjej-ship-it/workshop-prep-agent/commit/6fbd0bd5790d10305b6c70e02f1d14eb0764ef68) replaces whole-body buffering with incremental UTF-8 decoding and stream cancellation when the existing character limit is crossed. The remedy sits in the shared reader used by create, revise, advance and management routes; the create route was the measured runtime probe.

## Observed evidence

| Stage | Actual result |
|---|---|
| Installed baseline helper | 115 included files, 3 skips, **0 candidates**. JS/TS checks are lexical dynamic-evaluation matching only. |
| ChatNoir-guided source review | **1 confirmed low-severity finding**, 5 dismissed candidates. The finding came from agent review, not a baseline rule. |
| Same local 1 MiB stream before/after | Before: 1,048,576 bytes read, cancel=false. After: **262,144 bytes read, cancel=true**. Both returned 413; a small valid JSON control passed before and after. These byte counts describe this probe's chunks, not a new universal byte limit. |
| Regression tests | New streaming regressions failed on the original reader and passed after the fix. They cover absent/misleading Content-Length, smaller shared limits, split UTF-8, exact character limits, decoder flush, valid/invalid JSON and origin validation. |
| Existing app controls | 18 selected tests passed during the initial review. After adding 6 regressions, **24 focused tests passed**, including management authorization, origin/version checks, uploads and admission controls. Some database paths use mocks. |
| TypeScript and build | TypeScript checking and production webpack build passed on the patched source. |
| Report pipeline | The initial full local report passed validation, Markdown rendering and SARIF export. |
| Release | GitHub main and both changed source files matched the verified fix. Vercel reported success for Production deployment `7127788925` on exact commit `6fbd0bd5790d10305b6c70e02f1d14eb0764ef68`. A read-only `GET /api/config` returned HTTP 200 with JSON. |
| ChatNoir implementation | No new ChatNoir implementation defect surfaced; the code fix was in Workshop Prep Agent. |

The [public result ledger](e2e/separate-app-results.json) preserves the revisions and measured results. The app's [committed regression tests](https://github.com/fhajjej-ship-it/workshop-prep-agent/blob/6fbd0bd5790d10305b6c70e02f1d14eb0764ef68/tests/http-body.test.ts) are public. On a checkout with dependencies installed, run the affected checks in test mode with local storage and no production credentials:

```sh
WORKSHOP_MODE=test WORKSHOP_STORE=local node node_modules/tsx/dist/cli.mjs --test tests/http-body.test.ts tests/workshop-management.test.ts tests/material-upload.test.ts tests/generation-allowance.test.ts
npm run typecheck
WORKSHOP_MODE=test WORKSHOP_STORE=local npm run build -- --webpack
```

The evaluation reused installed dependencies; selected versions matched the public lockfile. No package installation, paid inference or live database call was used. Network calls were disabled in the request-stream probe. Only local synthetic inputs and disposable records were used in the tests. Full local reports and raw traces were not uploaded.

This was a bounded source review and in-process route test, not a blind or independent audit or complete deployed-HTTP security test. Body cancellation was verified locally; no oversized production request or memory-exhaustion attack was attempted. Effective upstream limits remain unverified. Zero baseline candidates did not close the review, and these results do not establish a detection rate or that every vulnerability was found.
