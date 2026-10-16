# Retained report contract

Use `chatnoir.report/v1` when saving a structured scan report. Start from the baseline helper output or `schemas/report.schema.json` in the repository. A copied skill remains self-contained: `scripts/chatnoir.py validate` enforces the essential contract without needing the root schema or third-party libraries.

The report contains `format`, `version`, `mode`, `target`, `coverage` and `findings`. Target identity records the digest of included file entries, Git revision/dirty state when available, inventory strategy, per-file hashes and skipped paths. Do not relabel a baseline inventory as reviewed source. `reviewed` and `deferred` describe the work actually completed for that mode. Retain baseline provenance when expanding it into an agent review; regenerate file identity if source changes.

Each finding has stable `id`, `rule_id`, human `title`, repository-relative `path`, positive `line`, `status`, `severity`, `confidence`, `evidence`, `attack_path`, `counterevidence`, `proof_gaps`, `remediation` and `validation` (`method`: `not_run`, `static` or `runtime`; `result`: explanation). Use a new `rule_id` for an agent finding outside the baseline rules, such as `AUTHZ-001`.

Statuses are `candidate`, `confirmed`, `dismissed`, `needs_review`, `fixed`, `still_vulnerable` or `inconclusive`. A confirmed/fixed verdict requires evidence, an attack path, an actual validation method and no decision-critical proof gaps. A dismissal requires positive counterevidence. Structural validation cannot verify truth, source line accuracy or sufficiency of reasoning; the reviewer owns those checks.

```sh
python3 <skill-dir>/scripts/chatnoir.py validate <report.json>
python3 <skill-dir>/scripts/chatnoir.py render <report.json>
python3 <skill-dir>/scripts/chatnoir.py sarif <report.json>
```

All helpers emit to stdout and do not write reports or upload SARIF themselves. Explicitly redirect to an output location outside the scanned tree to avoid contaminating its next inventory. Exit codes: 0 success (including zero **or nonzero** baseline candidates), 1 candidates with `scan --fail-on-candidates`, 2 invalid input or operational failure. Baseline success never means a security gate passed. SARIF keeps unresolved leads as `kind: review`, `level: note`; confirmed open findings use `kind: fail`. Dismissed/fixed findings are omitted. Uploading to a provider is a separate authorized action.
