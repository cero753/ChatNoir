# Browser sign-in and customer authorization evaluation

Observed October 16, 2026 using installed ChatNoir 0.1.2 in Codex desktop and Playwright CLI. This follows the [backend token/database evaluation](backend-evaluation.md) with two isolated headless Chrome sessions, actual sign-in forms, browser-issued customer session cookies and a fresh full-schema PostgreSQL database.

**One low-severity authentication finding was confirmed locally.** Its mechanism, source location, prerequisite details and reproducer remain in the local report while the private app finding is unfixed. No new ChatNoir implementation defect surfaced; no ChatNoir runtime patch or version bump was needed. The app source was left unchanged.

## Executed flows

Two synthetic customers completed the actual NextAuth email-code UI and reached their authenticated consoles. Email delivery used the app's built-in development simulation; the verifier, database and session cookies were not mocked. An invalid code was rejected before a legitimate code succeeded. This exercises the local email-code flow, not live delivery or production Clerk/Google sign-in.

**26 core authorization assertions passed**, with legitimate controls as well as adversarial requests using those browser-established cookies:

| Flow | Observed result |
|---|---|
| Own customer data | Both users could read their own team and sentinel records. |
| Foreign team and workspace | Foreign team reads, workspace switching and protected browser canonicalization returned 403. Own canonicalization returned 200. |
| Changed record workspace selector | Responses still contained only the authenticated caller's records, never the other user's sentinel. A 200 alone was not treated as a failed isolation boundary. |
| Foreign member role write | Both directions returned 404 for non-owner member targets in the other workspace. Legitimate own-member updates/restoration returned 200. |
| Anonymous/tampered customer session | Protected team reads returned 401. |

Additional checks confirmed that foreign write attempts left membership roles and sentinel record identities unchanged. The visible sign-out control cleared one user's session and protected access returned 401, while the other browser stayed authenticated. Transient loading-page navigation samples were not counted as decisive isolation checks; protected canonicalization and actual data results supplied the assertions.

The confirmed authentication finding is a separate result: passing these selected authorization checks does not erase it, and it does not establish complete customer isolation. The [aggregate ledger](e2e/browser-auth-results.json) records outcomes and limits. Private source, target identity/revision, endpoint names, raw traces and screenshots were not uploaded.

## Coverage and environment

The final runtime matched the pinned lockfile for Next 16.3.6, NextAuth 5.0.0-beta.32, Prisma 6.4.1, React 18.3.1 and jose 6.2.2; the generated Prisma schema also matched. Initial old-runtime and internal-plan fixture mismatches were corrected before the final assertions. Only synthetic database records and test secrets were used. External browser requests were blocked, and the final server network guard allowed only the isolated app/database ports. No packages were installed and no live mail/model credentials were present. The created browsers, server and database were stopped afterward. All included source-file hashes matched the initial browser-test snapshot.

The sparse source snapshot included 708 files and skipped 126: 100 absent sparse paths, 25 binary files and one excluded credential file. Its 104 broader heuristic leads are retained as `needs_review` outside this declared auth-flow focus; they were not silently dismissed or called vulnerabilities. The confirmed finding came from source-guided review and runtime validation, not a baseline rule. The full local report passed validation, Markdown rendering and SARIF export.

Production provider sign-in/exposure, every resource/invite/billing/outbound path, and stolen pre-logout cookie/global revocation remain untested. This is bounded owner-run evidence, not an independent or fully reproducible public benchmark or a security certification.
