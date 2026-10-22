# Synthetic incident exposure review

This offline example demonstrates a report workflow, not vulnerability detection
or a real incident investigation. The advisory, service, runtime versions and
worker are fictional. No PHP installation, Railway account, model, network or
credential is accessed. The service is an in-process stand-in; its version and
health responses do not establish anything about a real deployment.

From the source checkout, run with Python 3.10+ and choose a **new directory outside
this example**:

```sh
python3 examples/incident-review/demo.py --output-dir /tmp/chatnoir-incident-trial
```

The command writes `before.json`, `after.json` and matching Markdown reports. It
refuses to overwrite an existing directory. Expected observations:

| Asset/action | Before | After |
|---|---|---|
| Synthetic web runtime | Potentially affected: exact version in the fictional advisory | Not affected by that advisory: version in its fixed list |
| Update action | Planned | Verified by executing the local stand-in's health/version response |
| Background worker | Undetermined: no observation | Still undetermined |
| Worker observation action | Blocked | Still blocked |

The after result changes **only the local stand-in's state**. No actual runtime
package is upgraded, vulnerability exploited, credential rotated or deployment
verified. This example uses exact fictional version lists, not a general advisory
matching engine. The missing worker evidence prevents complete coverage or an
app-wide all-clear. The supplied advisory snapshot retains its original checked
date; service observation dates are the exercise date.

Use the existing helper to validate or export the generated report:

```sh
python3 skills/chatnoir/scripts/chatnoir.py validate /tmp/chatnoir-incident-trial/after.json
python3 skills/chatnoir/scripts/chatnoir.py client-report /tmp/chatnoir-incident-trial/after.json \
  --project "Synthetic incident exercise" --output /tmp/chatnoir-incident-trial/after.pdf
```

PDF export uses optional ReportLab if already installed. Core report validation
and Markdown output use only the standard library. No dependencies are installed
by the example. [Review workflow](../../skills/chatnoir/references/incident-review.md)
and [report contract](../../skills/chatnoir/references/report.md) describe real-project
evidence collection and authorization boundaries.

Verification:

```sh
python3 -B -m unittest discover -s tests -p test_incident_review.py -v
```
