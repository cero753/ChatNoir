# Fresh installed v0.2.2 sessions

Observed October 17, 2026. **Codex loaded the installed v0.2.2 skill and reproduced all three known HTTP-app vulnerabilities. Cursor's fresh request failed at its usage limit before inference.** Cursor loading and detection remain unverified in this run. [Source hashes and actual measurements](e2e/installed-0.2.2-results.json).

## Setup

Each native CLI received a separate fresh disposable copy of the [synthetic HTTP app](../examples/http-app/README.md), its intended contracts and a named installed ChatNoir fallback path. No project-local skill copy, expected finding labels or evaluator probe was supplied. This was a known-fixture test, not blind discovery or an unseen-app benchmark. All identities, tokens, invoices and documents were synthetic.

Both installed packages matched all 106 files from the v0.2.2 tag. Codex CLI 0.157.0 used the approved `gpt-6-sol` with high reasoning. Its native registry reported v0.2.2 installed and enabled; the session reported catalog discovery. Retained command events establish actual reads of the installed skill and review/evidence references, helper version 0.2.2 and a baseline scan.

Cursor CLI 2026.10.16-e3cb207 used its configured default without an override. Initialization reported Auto; the request returned the agent usage-limit error after 4.22 seconds, with zero successful model responses or skill reads. There was one request per host, with no retry, model/account switch, purchase or access workaround.

## What Codex caught

| Finding | Actual in-memory result | Remedy |
|---|---|---|
| Catalog SQL injection, `app.py:24–27` | Injected category returned all three products, including the unpublished draft; ordinary books/tools requests returned only their published items | Bind category as a query parameter |
| Cross-user invoice access, `app.py:28–36` | Alice's fake token retrieved Bob's invoice; an anonymous request was rejected | Restrict the invoice lookup to the authenticated owner |
| Download traversal, `app.py:37–40` | A traversal name returned the synthetic internal note; normal download returned the public fixture | Resolve and enforce containment under the public directory |

Codex executed nine in-memory dispatch checks after source inspection. The baseline emitted CN001 (`eval`) and CN004 (SQL) candidates only. The agent correctly dismissed the fixed `eval("2 + 2")` expression because request input cannot reach it; `/health` returned 4. Invoice ownership and path containment came from source-guided review and runtime reproduction, not additional deterministic rules.

## Fix controls and shipment

The evaluator separately ran the existing loopback HTTP probe against both supplied variants:

```sh
python3 scripts/http_probe.py examples/http-app/vulnerable
python3 scripts/http_probe.py examples/http-app/fixed
```

The vulnerable variant intentionally exited 1: three attack protections failed and five legitimate/authentication controls passed. The supplied fixed variant exited 0 with **all eight checks true**. Both native target snapshots remained unchanged. Neither fresh session generated a patch; the existing fixed app provided the negative control.

All **81 repository tests** and `scripts/demo.py` passed. No new ChatNoir scanner or skill runtime defect was found, so this follow-up publishes evidence and updates current compatibility wording without a package-version or release-asset change. v0.2.2 remains the current plugin release.

## Limits

These were fresh native CLI sessions, not another desktop UI/picker test. Unrelated optional connector startup authorization warnings appeared in Codex; no connector tool was called and the local review completed. Provider-backed inference used existing access, while the independent HTTP probe contacted loopback only. No production target, dependency installation, credential-content audit or adaptive attack round was included. Previous [v0.2.1 results](installed-0.2.1-e2e.md) and the [real coordinated-agent test](codex-coordinated-attack.md) remain separate evidence. Installation alone does not close Cursor's model-access gap.
