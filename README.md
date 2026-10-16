<p align="center">
  <img src="assets/logo.png" width="170" alt="ChatNoir black cat logo">
</p>

<h1 align="center">ChatNoir</h1>
<p align="center"><strong>Find the flaw. Prove the path. Verify the fix.</strong></p>
<p align="center">Security review for the code you ship.<br>One portable skill. Your coding agent. Evidence you can inspect.</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-111111"></a>
  <a href="https://github.com/fhajjej-ship-it/ChatNoir/releases"><img alt="Release v0.1.2" src="https://img.shields.io/badge/release-0.1.2-111111"></a>
  <a href="docs/compatibility.md"><img alt="Codex, Claude Code, Cursor" src="https://img.shields.io/badge/skills-Codex%20%C2%B7%20Claude%20Code%20%C2%B7%20Cursor-111111"></a>
</p>

You built the app. Now inspect the boundaries that matter: who can access another user's data, which inputs become commands or queries, and whether a fix closes the original hole.

**ChatNoir turns your coding agent into an evidence-first security reviewer.** It combines 15 review workflows with local scan helpers, attack-path reasoning, false-positive checks, fix verification, and portable reports. No ChatNoir account. No hosted scanner. No Python dependencies. Bring your existing agent and model.

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

For the IDE, use the project skill installer below, open that project, then type `/chatnoir` in a new agent conversation. This path was exercised through the native skill picker, review and remediation in Cursor 3.24.12. [Desktop test evidence →](docs/desktop-e2e.md) The package also includes Cursor's native plugin manifest; IDE marketplace/plugin installation remains unverified.

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

**The deterministic helper** inventories files, binds Git diffs, and emits leads from five rule families: dynamic evaluation, shell execution, unsafe deserialization, dynamic SQL and disabled TLS verification. Python uses AST matching. JavaScript/TypeScript have a narrow lexical dynamic-evaluation check. These are deliberately labeled **candidates**, with incomplete coverage.

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
