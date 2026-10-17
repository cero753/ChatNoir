# Local HTTP security fixture

This application is intentionally vulnerable teaching code. All records, tokens and files are synthetic. Do not deploy it. It requires only Python's standard library.

The intended contracts are:

- The public product catalog returns only published products in the selected category.
- A signed-in user can retrieve only their own invoice. `alice-test-token` and `bob-test-token` are deliberately fake local test identities.
- Downloads serve files inside `data/public/`; the sibling `data/internal/` directory is private application data.
- `/health` returns the value 4. Its constant expression is not caller controlled.

Run `python3 scripts/http_probe.py examples/http-app/vulnerable` from the repository root to exercise HTTP requests against an ephemeral loopback server. Use the `fixed` variant for negative controls. The probe exits 1 on a vulnerable variant and 0 when all three security boundaries and the legitimate controls pass. It never contacts an external target.

The fixture is designed to test the agent workflow, including authorization and file access that the eight-rule baseline does not automate. See the [fresh installed v0.2.2 results](../../docs/installed-0.2.2-e2e.md) and [release validation](../../docs/validation.md).
