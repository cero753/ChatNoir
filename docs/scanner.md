# Local scanner and report helpers

Run `python3 chatnoir.py --help` from the checkout, or the installed skill's `scripts/chatnoir.py` from anywhere. Python 3.10+ is required. Git is required for committed comparisons and used for inventories when the target is inside a repository. There are no third-party Python dependencies, network calls, package installations or target-code execution in these helpers.

| Rule | Python lead | CWE |
|---|---|---|
| CN001 | `eval` / `exec` | 95 |
| CN002 | Shell APIs, or subprocess calls with literal `shell=True` | 78 |
| CN003 | Pickle/dill/marshal loading and unsafe YAML loaders | 502 |
| CN004 | Query execution with directly constructed expressions | 89 |
| CN005 | Requests/httpx calls with literal `verify=False` | 295 |

AST matching recognizes straightforward import aliases. It is not type checking, interprocedural data flow or taint analysis. Rebindings can create false positives; wrapped calls, variable-built queries, computed keywords, custom loaders and indirect imports can be missed. Rule CN004 may flag a safe query-construction API and can miss unsafe SQL built in an earlier assignment. The JS/TS check matches only lexical `eval(...)` and `new Function(...)`; comments and strings can match. Agent validation is essential.

## Scope and privacy

Git inventory includes tracked and non-ignored untracked paths under the chosen target. Without Git, a directory walk is used; `.gitignore` is not interpreted. Common generated/dependency directories, Git metadata, credential filenames, binary/non-UTF-8 files, symlink files and oversized files are skipped. Directory symlinks are pruned and not traversed; they are not individually listed in walk inventories. Git submodule contents are not recursively audited. All such exclusions limit coverage.

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
