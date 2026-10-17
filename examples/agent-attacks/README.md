# Three agent-security demos

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 examples/agent-attacks/demo.py
```

This runs ChatNoir's real source scanner, then executes three deliberately vulnerable functions and their fixed counterparts. All identities, messages and note contents are synthetic. There is no model/API call, server, remote agent, credential use or network request. The export action appends a synthetic note to an in-memory list only. **Never deploy the vulnerable examples or permissive teaching executor.**

For the separate real Codex/Cursor review, live-input and cross-host message tests, see the [native agent evaluation](../../docs/live-agent-security.md). Its opt-in runner requires authenticated CLIs and makes provider inference requests; the command above remains fully offline.

Expected output:

```text
CHATNOIR / Synthetic agent trust-boundary demos
scan vulnerable: CN006 CN007 CN008 (candidates; runtime checks follow)
scan fixed: 0 candidates (not a security certification)
prompt_injection: local exports before=1; after=0; legitimate=PASS
tool_output: local exports before=1; after=0; legitimate=PASS
agent_to_agent: local exports before=1; after=0; legitimate=PASS
adversarial model proposal: denied; local exports=0
PASS: all three reproduced paths closed; legitimate controls preserved.
Synthetic scripted model only; no live LLM or swarm-protection benchmark.
```

Exit 0 means all measured before/after checks and legitimate controls passed. An unexpected scan result, broken fix, failed control or runtime error exits nonzero. `--json` emits actual results and source SHA-256 hashes. [Recorded results](../../docs/e2e/agent-security-results.json) are an executed fixture result, not a model-generated security verdict.

## The three boundaries

| Case | Vulnerable behavior | Fix and proof |
|---|---|---|
| Prompt injection / CN006 | Retrieved text containing an action instruction is appended as a system message. The scripted model proposes a synthetic note export and the application executes it. | Keep the document in a data role and authorize the proposed action using root-task capabilities. The legitimate summary works. A separate always-hostile proposer still cannot export. |
| Malicious tool output / CN007 | A tool's JSON response goes directly into an action dispatcher. Valid JSON containing an unauthorized action exports the note. | Validate proposal shape and authorize it against the receiving executor's trusted policy before dispatch. Malformed, extra-field and unauthorized proposals are denied; a valid summary works. |
| Agent-to-agent authority / CN008 | A peer claims to be the coordinator, supplies extra capabilities and asks the receiver to export. The receiver merges the peer's claims into authority. | Ignore self-granted capabilities and sender-role claims; use the root task's permissions. The export is denied and a legitimate peer summary works. |

Inspect [vulnerable entrypoints](vulnerable/app.py), [fixed entrypoints](fixed/app.py) and [the shared teaching runtime](runtime.py). The fixed entrypoints all use `Executor.authorize`, which validates the action against the immutable root-task allowlist before the permissive local sink. Bypassing the gate makes verification fail. This runtime is intentionally small and omits production tools, resource arguments, authentication, distributed message transport and remote agent compromise.

## Scan or review with ChatNoir

```sh
python3 chatnoir.py scan examples/agent-attacks/vulnerable
python3 chatnoir.py scan examples/agent-attacks/fixed
python3 -m unittest discover -s tests -p 'test_agent_security.py' -v
```

For an agent-guided review, ask your installed ChatNoir skill to review the vulnerable directory, trace document/tool/peer data into privileged actions, and validate only using the synthetic runner. See [agent review guidance](../../skills/chatnoir/references/agent-security.md) and the [precise scanner limits](../../docs/scanner.md). Scanning reads source without running it; the demo explicitly executes only the bundled fixtures.

The model is a deterministic role-sensitive stand-in, not an LLM. Moving text to a user/data role alone is not proof against real prompt injection; the adversarial-proposer test verifies the separate action gate. These known owner-authored fixtures demonstrate specific source patterns and executable authorization failures. They do not measure recall on unseen agents, adaptive attacks, large agent swarms or any provider's model safety, and ChatNoir does not install continuous runtime protection.
