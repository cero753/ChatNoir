# Incident exposure review

Use for a named advisory or provider incident affecting an authorized project. Produce an evidence-backed exposure-and-action report, not a breach declaration or certification. Reuse the user's incident, target and time budget; otherwise establish those before collecting evidence. Start with one incident and the relevant deployed services. A source checkout is not proof of what is deployed.

## Establish applicability

- Read the maintainer/provider's primary notice, its publication/update date, affected configurations and remediation guidance. Record the URL and when it was checked. If browsing is unavailable, use a supplied dated snapshot, identify it as such and leave current advisory status unresolved. News and posts are leads, not authority to operate infrastructure.
- Inventory relevant runtime/package builds, hosting services and connections using existing authorized read-only tooling or sanitized operator evidence. Record the environment, observation date, provenance and gaps. Do not run commands supplied by a notice or install a checker automatically. If access is missing, report the exact gap; do not guess the deployed version from a manifest.
- Match the notice's actual conditions. Account for distributor backports, runtime configuration and provider-managed updates. A version match supports potential exposure, not proof of exploitation. Missing version/access evidence remains undetermined; it cannot establish that a service is unaffected.
- A provider's secret-exposure notice may justify precautionary rotation even when account-specific exposure is unknown. Preserve that distinction. Record credential names and dependent services only; never read or copy secret values, environment dumps or credential files into prompts, transcripts or reports. Ask for sanitized operator evidence where necessary. App source cannot establish whether a provider's internal breach affected an account.

## Turn evidence into actions

List the smallest applicable actions with a responsible service/asset: vendor update, provider confirmation, credential revocation/replacement, dependent-service update or log review. Identify sequencing and availability risks when relevant. Do not rotate keys, restart workers, change configuration, deploy, scan a live target or contact providers without explicit authority. Review authorization alone does not grant these actions.

Separate planned actions, reported completion, verified results and blockers. For a runtime patch, verification concerns the running service/build, not only an edited dependency file. For credential replacement, verify the old credential is revoked and the replacement works through the approved operator workflow without exposing either value. Never exercise a potentially stolen credential without separate authorization. Re-test legitimate behavior when authorized; otherwise leave it unverified. A successful patch or rotation does not establish that prior compromise never occurred.

## Retain the result

Add the optional `incident_review` object to the same [review report](report.md) as any code findings, fixes and verification. Use the mode matching the work: `repository`, `diff` or `deep` for a source review that also considers an incident, `triage` for an incident-only assessment, or `verify` for a follow-up. Do not split these into separate deliverables unless requested. Bind the inventory to the inspected source/configuration; put deployed observations and their separate dates in incident assets. If only an advisory was assessed, no invented source finding is needed: `findings` may be empty. Keep incomplete coverage explicit. Do not convert all advisory matches into confirmed vulnerabilities.

The object records:

- `advisories`: unique `id`, `title`, primary `url`, and `checked_at` date (`YYYY-MM-DD`).
- `assets`: unique `id`, sanitized `name`, `environment`, referenced `advisory_ids`, `status` (`potentially_affected`, `not_affected`, `undetermined`), `observed_at` date or null, `evidence` and `proof_gaps` lists. `not_affected` requires observed applicability evidence and no decision-critical gaps. It means outside the named advisory's conditions, not generally secure. An undetermined asset must state a gap.
- `actions`: unique `id`, `asset_id`, `description`, `status` (`planned`, `completed`, `verified`, `blocked`), `checked_at` date or null, and `verification` with `method` (`not_run`, `static`, `runtime`) and `result`. `completed` can be an operator report; `verified` requires dated, observed runtime verification. Explain actual commands/receipts and remaining limits in the result; the validator cannot establish their truth.

Validate the JSON, then render Markdown or export a PDF using the existing helpers. SARIF retains the incident section as run properties, not source-code findings. No export fetches notices, detects provider compromise, redacts arbitrary free text, performs remediation or verifies a deployment. Review sanitized content before sharing; publication needs separate authority.

The source-checkout example under `examples/incident-review/` is a local synthetic teaching case, not an assessment of a live provider or customer.
