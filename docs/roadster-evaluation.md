# Real app: Roadster Reference

Observed October 16, 2026 using installed ChatNoir 0.1.2 in Codex desktop. The target was [Roadster Reference](https://github.com/fhajjej-ship-it/roadster-reference/tree/d37ada4bd81cd8228c4865286e24964e7e25c8fc), a separate Python-built static web app with browser JavaScript, pinned to commit `d37ada4bd81cd8228c4865286e24964e7e25c8fc`.

**Result: no confirmed vulnerabilities in this bounded review.** No new ChatNoir implementation defect surfaced, so no runtime patch was needed. A negative result belongs alongside the [Workshop Prep Agent finding and fix](separate-app-evaluation.md); it does not prove either app is secure or establish a detection rate.

## What actually ran

| Check | Observed result |
|---|---|
| Installed baseline helper | 32 included files, no file skips, **0 candidates**. Baseline rule coverage remains incomplete. |
| Guided source review | Renderer, URL handling, embedded JSON, local paths and execution boundaries reviewed; **4 hypotheses dismissed**, **0 vulnerabilities confirmed**. |
| Existing app tests | **9 tests passed**, including numeric and evidence-integrity controls. |
| Data and local-link validator | Passed against the original source data. |
| Static build | **17 HTML pages built** successfully. |
| Local security boundary checks | **6 passed** using actual renderer, validator and builder functions with synthetic inputs; output checked with Python `HTMLParser`. |
| ChatNoir report pipeline | Structured local report validated and exported as Markdown and SARIF. |
| Source preservation | Initial and final included-file hashes and snapshot digests matched. The target app was not patched. Git dirty state remained unknown because configured clean/process filters prevent the helper's safe status check. |

## What was challenged and why it was dismissed

- **Content/script injection:** raw HTML stayed escaped. A script-closing string inserted into a claim in a scratch copy remained inside the generated JSON; output contained only the two intended script elements. Browser data rendering uses `textContent` and created elements.
- **Active URL schemes or attribute injection:** the real Markdown destination function rewrote `javascript:` (including mixed case) and `data:` links to `#`. A quoted HTTPS URL stayed inside one `href` attribute. The actual source-registry validator rejected an injected JavaScript URL while accepting the original data. These are three distinct local controls.
- **Filesystem path escape:** a destination outside the repository root raised `ValueError` before use. The builder does not read linked target contents.
- **Server-side URL fetching:** source inspection traced external URLs to browser links. No server-side URL-fetch sink was identified in the reviewed code; this dismissal is static, not an observed network attack.

The six controls comprise raw HTML, active URL schemes, quoted HTTPS attributes, source-registry validation, outside-root paths and embedded JSON. They are successful negative controls, not six caught vulnerabilities.

The [structured result ledger](e2e/roadster-results.json) records the pinned revision, snapshot digest, control outcomes and limits. The app's existing checks can be run on that revision without packages or credentials:

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 tools/build.py
```

The review used a disposable public clone and a separate scratch copy for synthetic content. No production endpoint, dependency installation, paid inference or database was used. Repository metadata, templates and content are assumed maintainer-controlled; no public submission endpoint was identified. No browser execution, deployed-HTTP assessment, advisory lookup or secret-content scan was performed. Research claims and external sources were outside the security review. Raw local traces were not uploaded.
