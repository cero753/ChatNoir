# ChatNoir security review

Mode: repository · coverage complete: true
Snapshot: `21d9e3919e75e5ce4d1c175e6852c0942fa93dcd4434aa5ab982bf8923623d68`

Pattern matches are review leads. A zero-candidate baseline is not a clean bill of health.

## CN-0ea0d2408f06: SQL injection in the synthetic invoice lookup

confirmed · high · app.py:5

Evidence:

- app.py:4-6 interpolates the owner argument into SQL syntax.
- The included reproducer observed two invoice rows for the crafted owner value and one Alice row for legitimate input.

Attack path:

- A caller controls the owner value passed to invoices_for.
- String interpolation makes that value part of the WHERE clause.
- The crafted value changes the predicate and returns both synthetic owners' records.

Counterevidence:

- No HTTP route, authentication system or deployed service exists in this fixture; no external application reachability is asserted.

Validation (runtime): python3 examples/sql-injection/reproduce.py: vulnerable attack=2 rows, legitimate=1; fixed attack=0 rows, legitimate=1. All assertions passed.

Remediation: Bind the owner as a SQL value, as demonstrated in examples/sql-injection/fixed/app.py. Application callers must separately derive owner identity from an authorized principal.

## Coverage and limitations

Reviewed by this mode: 1 files. Deferred: 0. Skipped: 0.

- Declared scope: the synthetic invoice-query function only. No application, authentication, network, deployment or other database-engine assessment.
- Runtime check used in-memory SQLite and synthetic Alice/Bob invoice rows.
