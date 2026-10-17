# Local scanner and report helpers

Run `python3 chatnoir.py --help` from the checkout, or the installed skill's `scripts/chatnoir.py` from anywhere. Python 3.10+ is required. Git is required for committed comparisons and used for inventories when the target is inside a repository. There are no third-party Python dependencies, network calls, package installations or target-code execution in these helpers.

| Rule | Python lead | CWE |
|---|---|---|
| CN001 | `eval` / `exec` | 95 |
| CN002 | Shell APIs, or subprocess calls with literal `shell=True` | 78 |
| CN003 | Pickle/dill/marshal loading and unsafe YAML loaders | 502 |
| CN004 | Query execution with constructed expressions, including prior straight-line local assignments | 89 |
| CN005 | Requests/httpx calls with literal `verify=False` | 295 |
| CN006 | Dynamic content in a literal system/developer-role dictionary | 1427 |
| CN007 | Direct/straight-line `json.loads` data passed to a recognized action dispatcher | 862 |
| CN008 | Selected permission containers widened using subscripted permission fields | 807 |

AST matching recognizes straightforward import aliases. It is not type checking, interprocedural data flow or taint analysis. Rebindings can create false positives; wrapped calls, computed keywords, custom loaders and indirect imports can be missed. CN004 follows prior simple local assignments in the same statement block, respecting later reassignment and function boundaries. It does not trace branches, compound updates, object attributes, closures or cross-function query construction, and may flag a safe query-construction API. The JS/TS check matches only lexical `eval(...)` and `new Function(...)`; comments and strings can match. Agent validation is essential.

CN006 does not establish untrusted provenance or whether a dictionary is ever sent to a model; dynamic trusted policy can match. CN007 recognizes only `execute_action`, `dispatch_action`, `execute_tool`, `call_tool` and `dispatch`, with Python `json.loads` imports/aliases and simple local bindings. A validation wrapper can hide a genuinely unsafe flow; a downstream gate can make a flagged flow safe. CN008 recognizes `.update`, `.union` and `|=` on names ending in `capabilities`, `permissions`, `scopes`, `allowed_tools` or `allowed_actions`, with input subscript fields using those same names. Unrelated sets may match and differently named/framework-mediated flows may be missed. None of these rules proves attacker control or effective authorization. [CWE-1427](https://cwe.mitre.org/data/definitions/1427.html), [CWE-862](https://cwe.mitre.org/data/definitions/862.html) and [CWE-807](https://cwe.mitre.org/data/definitions/807.html) describe the mapped weakness classes. [Run the synthetic before/after cases](../examples/agent-attacks/README.md).

## Scope and privacy

Git inventory includes tracked and non-ignored untracked paths under the chosen target. Without Git, a directory walk is used; `.gitignore` is not interpreted. Common generated/dependency directories, Git metadata, credential filenames, binary/non-UTF-8 files, symlink files and oversized files are skipped. Directory symlinks are pruned and not traversed; they are not individually listed in walk inventories. Git submodule contents are not recursively audited and are ignored in dirty-state checks. If effective Git configuration defines a clean/process filter, the helper omits `git status` and returns `target.dirty: null` with `target.dirty_reason`; Git can execute those filters while comparing content. Source inventory and baseline review still proceed. Unknown dirty state is not a clean checkout. All such exclusions limit coverage.

Credential exclusion is based on filenames (`.env*`, private-key extensions and common credential names). It is **not a secret detector**: credentials can exist anywhere. Baseline findings omit source values, but filenames and other report data may still be sensitive. A report or SARIF file should be reviewed before publication or upload. Host agents may transmit inspected source to their model provider according to that provider's settings; ChatNoir cannot change that policy.

Bounds: 1 MiB per file, 64 MiB cumulative read budget and 20,000 paths. Narrow the target if inventory exceeds a total bound; the helper fails rather than silently claiming completion. Snapshot hashes cover included readable file bytes and paths, not excluded files or an atomic concurrent snapshot. Do not scan a directory under active hostile mutation; the helper is not a filesystem sandbox. For a final agent verdict, recheck evidence if source changed.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Command completed, including scans with candidates |
| 1 | Candidates found when `scan --fail-on-candidates` is supplied |
| 2 | Invalid input, unreadable report, failed Git command or operational bound |

No candidate count implies a security pass. Baseline `coverage.complete` is always false. A full declared-scope agent review may mark its work complete only when relevant deferred/skipped work is resolved or explicitly removed from its declared scope.

`validate` enforces essential field types and verdict invariants. It does not verify source truth or the semantic quality of evidence. SARIF uses review/note for unresolved leads and fail for confirmed open findings; it omits dismissed/fixed findings. No upload is performed. `diff` compares committed base/head IDs only; it never includes dirty or untracked changes automatically.

Imported report text is encoded as literal punctuation and line breaks are folded before Markdown rendering. This prevents report data from introducing links, headings or HTML; rendering is not a general-purpose HTML sanitizer for other inputs.
