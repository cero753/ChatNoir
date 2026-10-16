# Real-project self-audit

Observed October 16, 2026. ChatNoir was used on its actual repository at pre-fix commit `471a1087b5b28a77d813268ee723cf41a43c707c`, beyond its demo applications. The source-guided review found two defects in the shipped helper. Both are fixed in 0.1.2.

This was the existing owner's self-review, not an independent audit, blind benchmark or test of a third-party/customer application. ChatNoir's agent workflow identified the issues through source inspection; its five baseline rules did not detect them. The baseline returned five known teaching-example leads: three literal-evaluation false positives and two intentionally vulnerable SQL examples. Those examples were kept intact.

## Findings and executed proof

| Finding | Actual failure | Fix and result |
|---|---|---|
| Git filters executing during scan — medium, CWE-78 | `collect` called `git status` to record dirty state. With a clean/process filter configured and a tracked file needing comparison, Git ran the configured program. Tests created only a marker in a disposable directory. The same issue was reproduced through a nested repository's filter. | Query effective filter keys without executing their values. Skip status when clean/process filters exist; return `dirty: null` with `dirty_reason`. Ignore submodule content in permitted status checks. All three filter non-execution regressions pass. |
| Imported Markdown injection — low, CWE-116 | A crafted report used backslashes, bare URLs and newlines to create active links and a forged heading in rendered Markdown. Local parsing with preinstalled `marked 17.0.5` produced three links and the extra heading. No browser XSS or automatic image request was established. | Encode ASCII punctuation as literal character entities and fold embedded line breaks. The same parser produced zero links, zero images and no forged heading. Existing HTML handling and new backslash/newline checks pass. |

The Git attack requires an already-configured filter command/program, such as a project script changed by a contributor, or prepared local Git configuration. A `.gitattributes` file alone in an ordinary clone does not install that command. Content filters are a legitimate [Git feature](https://git-scm.com/docs/gitattributes); invoking them during a promised non-executing scan was the defect. Submodule exclusion follows the [status option's documented behavior](https://git-scm.com/docs/git-status).

Returning unknown dirty state is deliberately conservative: even an unused globally configured clean/process filter suppresses the status check. File inventory, hashes and source review still run. Unknown never means clean. Git configuration is not modified. This remains a stable-tree helper, not a sandbox for hostile concurrent mutation.

## Review and release checks

- Reviewed the shipped Python helper, convenience entrypoint, installer, report/schema contract, packaging metadata and security guidance. File reads, subprocess arguments, Git boundaries and imported-output handling were the main security surfaces. Application authentication, tenancy, billing and hosted endpoints are outside this local tool's implementation.
- Reproduced the defects against the pre-fix code and verified the remedies with harmless, local test inputs. The clean/process and Markdown regressions failed before the fix. Nested filter execution was separately reproduced before the fix.
- `python3 -m unittest discover -s tests -v`: **42 passed**. Tests isolate global/system Git configuration so local fixture policies are repeatable. Existing ignore handling, dirty state without filters, symlink/FIFO limits, CLI round trips and install controls remain checked.
- Ran the actual repository scan, report validation, Markdown export, SARIF export and demos. Native Claude plugin and marketplace manifest validation passed; this does not imply a successful Claude model session.
- [Structured verification report](e2e/real-project-review.json) records source hashes, original baseline dispositions, attack prerequisites, fixed verdicts and gaps. Its target inventory describes the working snapshot before publishing this report; it is not an atomic snapshot of the final release tree. Both fixed findings are omitted from its SARIF export as intended.

No new dependency, hosted scan, CI workflow or production probing was added. No private project source, account details or credentials were published. Windows/Linux behavior, unseen-app accuracy and broader independent security assurance remain unverified.
