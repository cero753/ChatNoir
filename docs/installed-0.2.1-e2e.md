# Fresh installed v0.2.1 sessions

Observed October 17, 2026 on macOS arm64. A fresh native Codex session loaded the installed ChatNoir v0.2.1 skill and reproduced all three known vulnerabilities in the [synthetic HTTP app](../examples/http-app/README.md). A fresh Cursor request stopped at its account usage limit before any model response. Cursor detection is therefore **unverified in this run**.

These are native CLI sessions, separate from the earlier [desktop/IDE tests](desktop-e2e.md) and [v0.1.1 harness results](harness-e2e.md). The [sanitized evidence ledger](e2e/installed-0.2.1-results.json) binds the tested source, installed skill and probe to SHA-256 digests. Raw traces remain private.

## Setup and loading

Each host received its own disposable copy of the vulnerable app and intended contracts. Neither received expected finding labels, the evaluator's probe or a project-local skill copy. The prompt named ChatNoir and supplied its installed path as an explicit fallback; this was not a blind skill-discovery test. All identities, tokens, invoices and files were synthetic.

Codex CLI 0.157.0 used the user's approved `gpt-6-sol` with high reasoning. Its native registry reported ChatNoir installed and enabled at 0.2.1. The session reported catalog availability, and retained command events show actual reads of the installed `SKILL.md`, review/evidence references, helper version and baseline. The tested installed resources matched the tagged source.

Cursor CLI 2026.10.16-e3cb207 used its configured default without a model override. Its installed package was v0.2.1, but the request returned the usage-limit error in 4.4 seconds. Initialization reported Auto; **zero successful model responses and no skill read** were observed. There was one request per host; no account change, purchase or quota workaround was attempted.

## What Codex actually caught

| Boundary | Observed runtime result | Smallest remedy |
|---|---|---|
| Category SQL injection, `app.py:24–26` | Injected category returned all three products, including unpublished product 2; ordinary books query returned only product 1 | Bind category as a query parameter |
| Cross-user invoice access, `app.py:28–36` | Alice's fake token retrieved Bob's invoice with HTTP-style status 200 | Query by both invoice ID and authenticated owner |
| Download traversal, `app.py:37–40` | `../internal/notes.txt` returned the synthetic private note | Resolve and enforce containment under the public directory |

The baseline supplied only CN001 (`eval`) and CN004 (SQL) candidates. Ownership and path containment came from source-guided review, not deterministic scanner rules. Codex dismissed the constant `eval("2 + 2")` because no request input reaches it; `/health` returned 4.

The agent inspected source before executing eight in-memory `app.dispatch` checks. Legitimate catalog, own-invoice and public-download requests worked, and an unauthenticated invoice request returned 401. Both target source snapshots remained unchanged. An initial shell heredoc could not create a temporary file in read-only mode; equivalent `python3 -B -c` checks succeeded without changing permissions. Unrelated configured connectors emitted authorization warnings at startup; no connector tool was used and the local review completed.

## Independent fix verification

The evaluator separately ran real loopback HTTP requests using the existing probe:

```sh
python3 scripts/http_probe.py examples/http-app/vulnerable
python3 scripts/http_probe.py examples/http-app/fixed
```

The vulnerable app intentionally exited 1: all three attack protections failed while five legitimate/authentication controls passed. The existing fixed app exited 0 with **all eight checks true**. This verifies the supplied fixes; it is not a claim that either fresh session generated a patch. No remediation request was made, and the deliberately vulnerable teaching app remains intact.

No new scanner or skill runtime defect was found. The fixture README's stale reference to five rule families was corrected to eight. All 75 repository tests and `scripts/demo.py` passed, as did source-digest, installed-resource and changed Markdown-link checks. ChatNoir remains v0.2.1; no replacement release package is needed for this documentation update.

## Limits and rerun

This is a known owner-authored fixture, not an unseen-app benchmark or security certification. No production target, dependency installation, credential-content audit or new desktop UI test was included. The native agents were authorized only for the disposable target and installed ChatNoir resources. Provider inference used existing accounts; the independent HTTP probe contacted loopback only.

Once normal Cursor agent access is available, start a fresh session with the installed plugin, provide a disposable copy and the intended contracts, and ask for source review with bounded local reproduction. Keep the evaluator probe outside the target. Until a model response and actual skill/tool evidence exist, installation alone must not be reported as a successful Cursor review.
