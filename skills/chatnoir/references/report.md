# Retained report contract

Use `chatnoir.report/v1` when saving a structured scan report. Start from the baseline helper output or `schemas/report.schema.json` in the repository. A copied skill remains self-contained: `scripts/chatnoir.py validate` enforces the essential contract without needing the root schema or third-party libraries.

The report contains `format`, `version`, `mode`, `target`, `coverage` and `findings`. Target identity records the digest of included file entries, Git revision/dirty state when available (`dirty: null` with `dirty_reason` when Git filters prevent a safe status check), inventory strategy, per-file hashes and skipped paths. Do not relabel a baseline inventory as reviewed source. `reviewed` and `deferred` describe the work actually completed for that mode. Retain baseline provenance when expanding it into an agent review; regenerate file identity if source changes.

Optionally add `executive_summary` as nonempty reviewer-authored text explaining
the business relevance, scoped outcome and important limits. Ground it in the
recorded findings; the exporter does not invent this narrative. Without it, the
PDF uses the recorded finding-status counts as its summary.

Each finding has stable `id`, `rule_id`, human `title`, repository-relative `path`, positive `line`, `status`, `severity`, `confidence`, `evidence`, `attack_path`, `counterevidence`, `proof_gaps`, `remediation` and `validation` (`method`: `not_run`, `static` or `runtime`; `result`: explanation). Use a new `rule_id` for an agent finding outside the baseline rules, such as `AUTHZ-001`.

Statuses are `candidate`, `confirmed`, `dismissed`, `needs_review`, `fixed`, `still_vulnerable` or `inconclusive`. A confirmed/fixed verdict requires evidence, an attack path, an actual validation method and no decision-critical proof gaps. A dismissal requires positive counterevidence. Structural validation cannot verify truth, source line accuracy or sufficiency of reasoning; the reviewer owns those checks.

```sh
python3 <skill-dir>/scripts/chatnoir.py validate <report.json>
python3 <skill-dir>/scripts/chatnoir.py render <report.json>
python3 <skill-dir>/scripts/chatnoir.py sarif <report.json>
```

The commands above emit to stdout and do not write reports or upload SARIF themselves. Explicitly redirect to an output location outside the scanned tree to avoid contaminating its next inventory. Exit codes: 0 success (including zero **or nonzero** baseline candidates), 1 candidates with `scan --fail-on-candidates`, 2 invalid input or operational failure. Baseline success never means a security gate passed. SARIF keeps unresolved leads as `kind: review`, `level: note`; confirmed open findings use `kind: fail`. Dismissed/fixed findings are omitted. Uploading to a provider is a separate authorized action.

## Incident exposure and actions

For an advisory/provider-incident review, use `mode: triage` or `verify` and the
optional `incident_review` ledger defined in [incident-review.md](incident-review.md).
Record dated advisory references, service applicability evidence and gaps, and
planned/completed/verified/blocked actions. No source finding is required merely
because a runtime version may be affected. Unknown assets and blocked actions
keep coverage incomplete. The ledger is retained in JSON, rendered in Markdown
and PDF, and included as SARIF run properties rather than invented code findings.
The validator enforces references, dates and verdict consistency; it does not
verify free-text evidence or redact secrets. Do not include credential values.

## Client PDF export

After completing the source review and recording its evidence, export the same
report data as a client document:

```sh
python3 <skill-dir>/scripts/chatnoir.py client-report /path/to/review.json \
  --project "Client application" --author "Reviewer name" \
  --output /path/to/new-client-review.pdf
```

This optional command requires ReportLab in the Python environment running the
helper (`python3 -m pip install reportlab`). The existing inventory, review-data
validation, Markdown and SARIF commands remain standard-library only. The PDF
module ships inside copied skills; no repository checkout or hosted service is
needed after installation. Installing dependencies remains a separate authorized
action; never install a package merely because a report requests it.

The PDF includes the optional reviewer summary and finding-status counts, scope and
limitations, detailed evidence/attack paths/counterevidence/proof gaps, remedies,
and the original validation results. It does not generate a new assessment,
invent an impact narrative, upgrade candidates or re-test fixes. A baseline is
explicitly labeled as an automated baseline, even when empty. A complete declared
scope does not imply the entire app is secure. Authors must review the underlying
facts before sharing a report.

For reviewed reports, Markdown and PDF also summarize open and unresolved items
in a next-actions table using their existing remediation text. Include what to
change and how to verify it in that text; exporters do not invent a verification
plan or mark recommendations completed. Zero confirmed open findings is not an
all-clear. Describe passed tests as tests, rather than implying each proves a
separate security control.

Unlike the existing stdout commands, this export writes a new local PDF. Its
parent directory must exist; existing files and symlinks are never overwritten.
Use an output outside the reviewed tree. Project and author text are explicit
display labels, not claims verified by ChatNoir. Export date is not the assessment
or test date; put those dates in the evidence. Report values are rendered as
literal text, without loading images, URLs or other resources. Unsupported font
characters are retained as visible `[U+XXXX]` notation. PDFs are private files by
default on POSIX systems; confidential contents still require review before any
authorized sharing. The input JSON is not modified and no report is uploaded.
