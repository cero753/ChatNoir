<p align="center">
  <img src="assets/logo.png" width="170" alt="ChatNoir black cat logo">
</p>

<h1 align="center">ChatNoir</h1>
<p align="center"><strong>Protect what you build from agent attacks.</strong></p>
<p align="center">Find security gaps. Reproduce attack paths. Verify the fixes.<br>One portable skill. Your coding agent. Evidence you can inspect.</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-111111"></a>
  <a href="https://github.com/fhajjej-ship-it/ChatNoir/releases/latest"><img alt="Release v0.2.2" src="https://img.shields.io/badge/release-0.2.2-111111"></a>
  <a href="docs/compatibility.md"><img alt="Codex, Claude Code, Cursor" src="https://img.shields.io/badge/skills-Codex%20%C2%B7%20Claude%20Code%20%C2%B7%20Cursor-111111"></a>
</p>

[Download v0.2.2](https://github.com/fhajjej-ship-it/ChatNoir/releases/download/v0.2.2/chatnoir-0.2.2.zip) · [SHA-256 checksum](https://github.com/fhajjej-ship-it/ChatNoir/releases/download/v0.2.2/SHA256SUMS-0.2.2)

You built the app. Now inspect the boundaries that matter: who can access another user's data, which inputs become commands or queries, and whether a fix closes the original hole.

**ChatNoir turns your coding agent into an evidence-first security reviewer.** It combines 15 review workflows with local scan helpers, attack-path reasoning, false-positive checks, fix verification, and portable reports. No ChatNoir account. No hosted scanner. No Python dependencies. Bring your existing agent and model.

Review how retrieved content, tool outputs and peer messages reach privileged actions. The published tests verify specific application fixes; continuous runtime blocking and broad swarm protection remain unproven. [Measured agent-attack results and limits →](docs/live-agent-security.md)

**Early public release:** verified Codex reviews and bounded synthetic attack/fix tests are available. Claude model access and the latest Cursor agent run remain blocked; adaptive same-agent attack rounds have not run. [Launch status and exact limits →](docs/launch-readiness.md)

## Try it in a minute

Python 3.10+ and Git are enough for the demos. No API key or model call is needed.

```sh
git clone https://github.com/fhajjej-ship-it/ChatNoir.git
cd ChatNoir
python3 scripts/demo.py
```

Actual output from the included synthetic fixtures:

```text
CN004 CWE-89: Dynamically constructed SQL
app.py:5 | candidate | validation: not_run

vulnerable: attack=2 rows; legitimate=1 row
fixed: attack=0 rows; legitimate=1 row
Runtime boundary check: PASS (synthetic in-memory SQLite).
```

The demo also challenges a false positive and binds a committed patch to exact revisions and a SHA-256 digest. [See the full recorded run and examples →](docs/demos.md)

For real HTTP boundary checks, [the local application fixture](examples/http-app/README.md) demonstrates SQL injection, cross-user invoice access and file traversal, with fixed controls. All data is synthetic.

**Fresh installed v0.2.2 check:** Codex loaded the installed skill, reproduced all three HTTP-app flaws and dismissed the constant `eval` candidate. Independent HTTP verification passed all eight checks on the fixed app. The fresh Cursor request hit its account usage limit before inference, so its loading and detection remain unverified in this run. [Results, commands and access limits →](docs/installed-0.2.2-e2e.md)

## Agent attack demos: catch, reproduce, verify

```sh
python3 examples/agent-attacks/demo.py
```

ChatNoir flags three source-level leads, and the runner verifies their actual synthetic effects:

| Boundary | Before | After |
|---|---|---|
| Retrieved text promoted into privileged instructions | 1 local note export | 0; legitimate summary works |
| Malicious tool JSON dispatched as an action | 1 local note export | 0; legitimate summary works |
| Peer-supplied capabilities widen another agent's authority | 1 local note export | 0; legitimate summary works |

The fixed action gate also denies an always-hostile model proposal. Everything runs locally with synthetic data, an in-memory action sink and a **scripted model**. This demonstrates specific application boundaries, not real-model prompt-injection resistance, protection against arbitrary swarms or continuous runtime blocking. [Source, exact output, tests and limits →](examples/agent-attacks/README.md)

**Tested with real Codex and Cursor agents:** both loaded ChatNoir, confirmed all three flaws and verified the supplied fixes. Separate live agents resisted all six sampled hostile inputs. Real peer messages were exchanged in both directions; replaying each malicious producer message into the app caused **1 synthetic export before the fix and 0 afterward**, while legitimate summaries worked. No native-agent compromise or general swarm protection was demonstrated. [Runnable native evaluation, measured results and limits →](docs/live-agent-security.md)

**Coordinated approval laundering:** a separate two-peer quorum fixture reproduces **1 synthetic export before → 0 after**, with single-peer, duplicate-sender and legitimate controls. A real Codex ChatNoir review confirmed the authorization flaw even though the scanner returned zero candidates. The mixed Codex/Cursor chain remains **incomplete because Cursor hit its agent usage limit**. [Runnable coordinated case, measured evidence and access gap →](docs/coordinated-agent-security.md)

A fresh Codex session using **installed v0.2.1** also reproduced this flaw, verified the supplied fix and restored the export by bypassing only the gate in memory. Legitimate summaries still worked. This was one real reviewer executing synthetic peer messages, not a completed live multi-agent chain. [Installed-package verification →](docs/coordinated-agent-security.md#fresh-installed-v021-follow-up)

**Completed with multiple real Codex agents:** seven fresh sessions authored and handed off their own attack/endorsement messages, ran a legitimate control, and reviewed the app with ChatNoir. Replaying those exact hostile messages caused **1 synthetic export before → 0 after**; legitimate summaries worked. The real coordinator chose `summarize`, so no native-agent compromise was demonstrated. [Runnable all-Codex test, actual messages and fix proof →](docs/codex-coordinated-attack.md)

## Real app: Workshop Prep Agent

On October 16, 2026, ChatNoir 0.1.2 guided a security review of [Workshop Prep Agent](https://github.com/fhajjej-ship-it/workshop-prep-agent), a separate TypeScript/Next.js app, in Codex desktop. It found a **low-severity request-body buffering weakness (CWE-400)**: `lib/http.ts` read the entire JSON stream before enforcing its size limit.

**The fix:** replace whole-body buffering with incremental UTF-8 decoding and cancel the stream as soon as the existing character limit is exceeded. Valid JSON, split Unicode characters and existing origin checks retain their behavior. [Shipped patch and regression tests →](https://github.com/fhajjej-ship-it/workshop-prep-agent/commit/6fbd0bd5790d10305b6c70e02f1d14eb0764ef68)

The same local 1 MiB ASCII request exercised the actual create route, configured for a 250,000-character limit:

| Observed behavior | Before | After |
|---|---|---|
| Bytes read from the test stream | 1,048,576 (entire body) | 262,144 (stopped early) |
| Stream cancelled | No | Yes |
| Response | 413 | 413 |
| Small valid JSON control | Passed | Passed |

**Verification:** new regression tests reproduced the failure before the fix; all **24 focused app tests**, TypeScript checking and the production webpack build passed afterward. The automatic production deployment succeeded on the exact fix commit, and a read-only `/api/config` smoke check returned HTTP 200.

The baseline helper returned **zero candidates**; this finding came from ChatNoir's agent-guided source review and local validation. Five suspected issues were dismissed. Body cancellation was verified with local `Request` streams; no oversized production request or memory-exhaustion test was attempted. Practical production denial-of-service impact was not established. [Full case, revisions and verification commands →](docs/separate-app-evaluation.md)

A second real-app review covered [Roadster Reference](docs/roadster-evaluation.md), a Python-built static web app. It produced **no confirmed vulnerabilities**: 9 existing tests, the 17-page build and 6 local security boundary controls passed. Four review hypotheses were dismissed with evidence; no ChatNoir code fix was needed. This bounded negative result is not a security certification.

A [backend/auth/database evaluation](docs/backend-evaluation.md) then exercised a private FastAPI app with real service-token/JWT verification and fresh PostgreSQL. **18 API integration checks passed**, covering invalid credentials, JWT bypass attempts, SQL injection text and worker workspace consistency. No vulnerability or new ChatNoir defect was confirmed in that scope. That run excluded browser sign-in and complete customer authorization.

## Real app: a private SaaS application

On October 16–17, 2026, ChatNoir guided a review and remediation of a private SaaS application with a backend, customer authentication, workspace authorization and PostgreSQL. **An email-code race was reproduced and fixed; dependency remediation finished with zero `npm audit` findings.** The application is anonymized; detailed source and release records remain private.

### Email-code race: one code could create two sessions

Two concurrent sign-in requests could both read the same unused email code before either marked it consumed. Actual NextAuth callbacks in two independent browser contexts produced **two authenticated sessions from one code**, even though later sequential replay was rejected. This was rated **low severity**: it violated the single-use guarantee but required possession of a valid code; it did not demonstrate sign-in without credentials or cross-user data access.

**The fix:** atomically claim the code in PostgreSQL before creating an identity/session. The update must match an unused, unexpired code below the attempt limit, and only a request that updates exactly one row can proceed.

**Run the public reproduction** (Python 3.10+, no dependencies or accounts):

```sh
python3 examples/email-code-race/demo.py
```

It reproduces multiple sessions before the fix and exactly one after it, with replay and legitimate sign-in controls. [Demo source, expected output and limits →](examples/email-code-race/README.md) This independently written synthetic SQLite fixture illustrates the same race; the real app's PostgreSQL/NextAuth results are below.

| Verification | Before | After |
|---|---|---|
| PostgreSQL regression forcing both verifiers to read the unused code | 2 successful verifiers; regression failed | 1 successful verifier |
| Actual NextAuth callbacks in 2 independent browser contexts | 2 authenticated sessions | 1 authenticated session |
| Actual NextAuth callbacks in 8 independent browser contexts | Not measured | 1 authenticated session |
| Sequential replay / fresh legitimate sign-in | Rejected / succeeded | Rejected / succeeded |

Expired codes, exhausted attempts, repeated incorrect codes, and expiry/attempt changes between reading and claiming also passed regression checks. The [initial pre-remediation browser evaluation](docs/browser-auth-evaluation.md) separately recorded **26 passing authorization assertions**, including selected cross-user reads/writes. Those held boundaries did not cancel out the race finding.

### Dependency vulnerabilities: audit evidence, then compatibility proof

The release's `npm audit` gate flagged vulnerable dependencies. Compatible patches to **Next.js 16.3.8, Sharp 0.35.5 and source-map-js 1.2.2** reduced the audit's high/critical counts to zero. The remaining **10 moderate package findings** propagated from two underlying advisories: selector-parser CPU exhaustion and `sprintf-js` denial of service. These were vulnerable-version matches; app-level exploitability of the dependency advisories was not established.

**The fix:** pin `postcss-selector-parser` to **7.1.6** within the typography dependency, and remove the vulnerable `sprintf-js` chains using **argparse 2.0.1** and **global-agent 4.1.3** overrides. The existing content parser and browser model library were retained; no advisory was suppressed.

**Verification:** a clean install and both installed-tree and lockfile audits reported **0 vulnerabilities at every severity**. Four focused compatibility tests passed for YAML parsing/CLI behavior, typography selector handling, HTTP proxy bootstrap and HTTPS CONNECT routing. Three existing content tests passed; all **12 actual content files** retained identical parsed metadata/bodies, and all generated typography components/variants matched their previous output. CUDA/model downloads and model inference were not tested.

### Shipped and checked

Both fixes passed exact-revision correctness/security reviews, required CI and production builds. The reviewed artifacts were promoted to production; staged and production smoke checks, Vercel runtime-error checks and Sentry release-health checks passed.

The race came from **ChatNoir's agent-guided source review and runtime validation**; dependency findings came from the separately available **`npm audit`**, not ChatNoir's baseline rules. Detailed source and release receipts remain private. Tests used local synthetic accounts and disposable PostgreSQL; no production exploit was demonstrated. Live mail delivery, production Clerk/Google sign-in and complete customer isolation remain unverified. This is bounded owner-run evidence, not a security certification. No new ChatNoir runtime defect was found in this evaluation.

## Install where you build

**Claude Code plugin**

```text
/plugin marketplace add fhajjej-ship-it/ChatNoir
/plugin install chatnoir@chatnoir-marketplace
```

Then start a fresh session and invoke `/chatnoir:chatnoir`, or ask Claude to use ChatNoir for a security review.

**Codex plugin**

```sh
codex plugin marketplace add fhajjej-ship-it/ChatNoir
codex plugin add chatnoir@chatnoir-marketplace
```

Open a fresh session and ask Codex to use ChatNoir. Clients with a plugin directory can use the repository marketplace; client capabilities vary. This is a community GitHub distribution, not an official directory listing.

**Cursor plugin**

For a local plugin session with Cursor CLI:

```sh
cursor-agent --plugin-dir /absolute/path/to/ChatNoir
```

For the IDE, use the project skill installer below, open that project, then type `/chatnoir` in a new agent conversation. This path was exercised through the native skill picker, review and remediation in Cursor 3.24.12. [Desktop test evidence →](docs/desktop-e2e.md) Native desktop plugin installation, version 0.2.2 and the updated descriptions were subsequently checked separately; the latest fresh Cursor model request hit its usage limit before inference. Installation does not establish a successful model review. [Current compatibility →](docs/compatibility.md)

**Codex, Cursor, Claude Code, or another Agent Skills host**

From your ChatNoir checkout, copy the self-contained skill into an existing project:

```sh
python3 scripts/install.py --harness codex --project /path/to/your-app
python3 scripts/install.py --harness cursor --project /path/to/your-app
python3 scripts/install.py --harness claude --project /path/to/your-app
```

Choose **one** matching your host. Installation refuses to overwrite an existing skill. For other hosts, copy `skills/chatnoir/` into their documented skill directory or load `SKILL.md` and its linked references manually. Host support for files, terminal tools and skills is required. [Compatibility and installation details →](docs/compatibility.md)

## Ask better security questions

```text
Use ChatNoir to review this repository for security vulnerabilities.
Focus on authentication, tenant isolation, uploads and outgoing requests.
Keep the review read-only. Show attack paths and evidence for each finding.
```

```text
Use ChatNoir to review the diff from main to this branch.
Explain security regressions, affected callers and important coverage gaps.
```

```text
Use ChatNoir to investigate this finding. If confirmed, fix the shared
enforcement boundary and verify the original trigger plus legitimate behavior.
```

## What you get

| Capability | What it produces |
|---|---|
| Repository, scoped and diff review | Findings tied to inspected paths and declared coverage |
| Deep review and discovery | A bounded second pass over the same scope; independent workers only when available and allowed |
| Validation, attack paths and triage | Evidence, counterevidence, preconditions and an explicit verdict per candidate |
| Fixing and fix verification | A requested minimal patch, or a read-only assessment of whether the original boundary is closed |
| Threat modeling and policy | Assets, actors, trust boundaries, invariants and explicit unknowns |
| Patch risk and hardening | Source-backed tradeoffs, relevant checks, recovery and proportionate remedies |
| Writeups and tracking | A self-contained vulnerability report or local issue draft; external writeback only when authorized |

[All 15 workflows and their implementation boundaries →](docs/capabilities.md)

## A skill and a scanner, with clear jobs

**The skill** guides your agent through source review across languages it can inspect. It supplies the workflow; your host supplies the model and tools. Review quality varies with those capabilities.

**The deterministic helper** inventories files, binds Git diffs, and emits leads from eight rule families: dynamic evaluation, shell execution, unsafe deserialization, dynamic SQL, disabled TLS verification, dynamic privileged-role prompts, decoded action dispatch and message-supplied permission merges. Python uses AST matching. JavaScript/TypeScript have a narrow lexical dynamic-evaluation check. These are deliberately labeled **candidates**, with incomplete coverage.

```sh
python3 chatnoir.py scan /path/to/your-app
python3 chatnoir.py inventory /path/to/your-app
python3 chatnoir.py diff /path/to/your-app --base main --head HEAD
```

For saved output, redirect outside the scanned tree, then validate, render or export:

```sh
python3 chatnoir.py scan /path/to/your-app > /path/to/review.json
python3 chatnoir.py validate /path/to/review.json
python3 chatnoir.py render /path/to/review.json
python3 chatnoir.py sarif /path/to/review.json
```

ChatNoir does not certify an app as secure. It has no comparative benchmark or established detection rate. A zero-candidate result is not a clean bill of health. Dependency auditing and secret-content detection require separately available tools. [Rules, exclusions and limits →](docs/scanner.md)

## Built to be inspected

- Standard-library Python helpers; no install hooks, background processes or automatic uploads.
- Source values are omitted from baseline findings; credential filenames are excluded.
- Structured JSON, readable Markdown and SARIF 2.1.0 exports preserve unresolved leads as review items.
- Real vulnerable/fixed fixtures, negative controls, and tests for file handling, Git boundaries, reporting and installation.

```sh
python3 -m unittest discover -s tests -v
```

[Separate-app evaluation →](docs/separate-app-evaluation.md) · [Real-project self-audit and fixes →](docs/real-project-audit.md) · [Validation evidence →](docs/validation.md) · [Contributing →](CONTRIBUTING.md) · [Report a vulnerability privately →](SECURITY.md) · [MIT license →](LICENSE)

*Chat noir* is French for *black cat*. Quiet, watchful, and curious about the places a boundary can break.
