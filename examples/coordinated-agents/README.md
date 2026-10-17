# Coordinated peer approval laundering

Two distinct peers agree on an action outside the original user's task. A flawed receiver treats their quorum as authorization. The receiving application's fix checks the root task's immutable allowlist before the action sink.

This is a deliberately small synthetic application, not a production agent framework. All notes, identities, task IDs and messages are invented. `export_note` appends a synthetic string to an in-memory list; no file is exported and no service receives data. Never deploy the vulnerable entrypoint or permissive teaching executor.

## Offline reproduction

```sh
python3 examples/coordinated-agents/demo.py
```

Observed output:

```text
Coordinated synthetic approval laundering
two agreeing peers: vulnerable exports=1; fixed exports=0, denied
single peer / duplicate sender: denied in both variants
legitimate two-peer summary: PASS in both variants
PASS; offline fixture only, no live agents or distributed transport
```

`--json` returns the actual measurements. Exit 0 requires the vulnerable export, fixed denial, working legitimate summaries and single/duplicate-peer denials. Bypassing the fixed authorization gate makes verification fail. Wrong-task, denied and conflicting-action endorsements are covered by focused tests.

Inspect the [vulnerable](vulnerable/app.py) and [fixed](fixed/app.py) functions. Both require two distinct sender strings agreeing on the same task and action. Those checks alone cannot create authority. The fixed function additionally calls the shared [teaching runtime](../agent-attacks/runtime.py)'s `Executor.authorize`. Sender strings and a parent's SHA-256 digest provide test linkage, not authenticated identities or a trusted approval signature.

The deterministic scanner returns **zero candidates in both variants**: its narrow permission-merge rule does not recognize a quorum-to-dispatch policy error. This case requires ChatNoir's agent-guided source review and runtime validation; zero candidates are not a clean bill of health.

A [fresh Codex review using installed ChatNoir v0.2.1](../../docs/coordinated-agent-security.md#fresh-installed-v021-follow-up) confirmed the flaw, verified the supplied fix and observed the export recur when the authorization gate alone was bypassed in memory. This single-reviewer test used synthetic peer messages; the mixed-host chain remains separate and incomplete.

## Opt-in real agents

For a completed **all-Codex** test with model-authored attack arguments and actual file handoffs:

```sh
python3 scripts/codex_coordinated_eval.py \
  --output /tmp/chatnoir-real-codex-NEW \
  --skill-path /absolute/path/to/installed/skills/chatnoir
```

This separate POSIX runner makes up to seven native Codex requests and loads your explicitly selected installed skill for review (with matching helper/reviewer/scan versions). It verifies actual input reads, message lineage, application effects, legitimate controls and the reviewer's runtime gate proof. [Measured results, exact synthetic messages and limits](../../docs/codex-coordinated-attack.md). The coordinator resisted the attack; replaying the actual producer messages exposed the app flaw and confirmed its fix. This does not fill the mixed-host gap below.

With existing authenticated Codex and Cursor CLIs on a POSIX host:

```sh
python3 scripts/coordinated_agent_eval.py --output /tmp/chatnoir-coordinated-NEW
```

Use a new output directory. The runner makes up to ten provider calls using your existing inference quota/billing: a Codex analyst, a Cursor endorser that reads its actual message, and two native coordinators per hostile/legitimate case, followed by one ChatNoir source/fix review per host. Codex defaults to the previously user-approved `gpt-6-sol` with high reasoning (`--codex-model` can select another available model); Cursor uses its configured default. No sign-in, installation, purchase or global configuration change is performed.

The second message contains the SHA-256 of the actual first message. Both native coordinators read the same resulting bundle. Separately, the exact producer messages run through both application variants and single/duplicate-peer controls. Prescribed producer outputs are known synthetic fixtures; coordinator resistance is separate from ChatNoir's review. It is never reported as ChatNoir runtime blocking.

Failures retain a non-pass, stop dependent scenarios and skip further requests to a host whose call failed. There are no automatic retries, model switches or provider-policy bypasses. Workspaces remain outside the repository; raw transcripts and account metadata stay local and must not be published wholesale. `results.json` records skipped stages and `checks_passed`; incomplete runs exit nonzero. Missing executables can terminate setup.

The [current measured results and limits](../../docs/coordinated-agent-security.md) distinguish completed model requests, blocked access, offline checks and any unexecuted mixed-host steps. These are local file handoffs, not authenticated distributed transport, autonomous collusion, an adaptive attack campaign or a large-swarm benchmark.
