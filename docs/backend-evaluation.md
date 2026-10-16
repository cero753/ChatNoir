# Real backend, authentication and database evaluation

Observed October 16, 2026 with installed ChatNoir 0.1.2 in Codex desktop. The target was an existing private application with a FastAPI backend, service-token authentication, signed privileged JWTs and PostgreSQL-backed resources. Its exact revision, private source, endpoint names and raw traces remain local. The public summary is therefore not a fully reproducible benchmark.

**Result: no vulnerabilities confirmed in the selected backend paths.** Four hypotheses were dismissed with runtime counterevidence. No new ChatNoir implementation defect surfaced, so no runtime patch or version bump was needed. These outcomes extend the [static-app review](roadster-evaluation.md) with actual authenticated API/database execution, while remaining separate from the [confirmed Workshop Prep Agent finding](separate-app-evaluation.md).

## What actually ran

The real, unpatched app middleware and route handlers ran through HTTPX `ASGITransport`. They used real signature/expiry verification and real asyncpg queries against a fresh PostgreSQL 17 instance. Credentials, auth verification, queries and returned rows were not mocked. There was no socket HTTP server or browser sign-in in this run.

| Boundary | Observed result |
|---|---|
| Service authentication | Missing/wrong tokens returned 401 before DB initialization. Configured primary, fallback and bearer credentials succeeded. |
| Privileged JWT verification | Missing, forged, expired, unsigned and wrong-role tokens returned 401. A valid signed token reached the offline-provider guard without calling a model. |
| Stored-resource access | An unauthenticated read returned 401. A legitimate parameterized read returned one expected synthetic row. SQL injection text stayed a bound value and returned zero rows. |
| Worker identity | The real DB lookup resolved the expected workspace. A mismatched workspace/lead/workflow was rejected with 409 before model execution. This checks worker consistency, not every end-user tenant authorization path. |
| Data preservation | Both synthetic message rows and the single workflow row remained unchanged after negative controls. |

**18 checks passed** in total, including positive controls. The database held minimal synthetic tables for the exercised queries; this was not a full production-schema migration. Startup/model workflows were outside scope. The valid-token control verifies passage through authentication, not a successful model conversation.

The installed baseline included **23 files**, skipped **2 binary files** and returned **0 candidates**. Guided review supplied the semantic reasoning; absence of baseline candidates did not close the assessment. The full private report passed ChatNoir validation, Markdown rendering and SARIF export. Initial/final included-file hashes and the staged runtime Python bytes matched; the target app was not patched.

## Containment and limits

The run reused existing local runtime images and a fresh database on a dedicated internal Docker network. Source and probe mounts were read-only; production data/configuration and credentials were not mounted. No host ports were published. The environment contained synthetic secrets, with model/email credentials absent. The created containers and network were removed afterward. Five selected dependency versions matched the target requirements; the [result ledger](e2e/backend-results.json) records them and the aggregate outcomes.

No browser/identity-provider sign-in, frontend user-membership authorization, complete startup, live model workflow, production endpoint, billing/mail integration, dependency-advisory or secret-content scan was tested. No package installation, paid inference or external database call was used. The backend's shared service authority is not an end-user session; these checks do not establish complete customer tenant isolation. This bounded negative result is not security certification, a detection-rate estimate or an independent audit.

A subsequent [local browser/customer authorization evaluation](browser-auth-evaluation.md) exercises selected UI sign-in and cross-user flows that were outside this backend-only run. Its finding and coverage limits are recorded separately.
