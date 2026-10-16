# Writeups and tracking

## Vulnerability writeup

Pin the assessed source/version and preserve the original claim. If exact source is unavailable, make the assessment conditional and say which claims cannot be checked. Produce a self-contained report with title, affected component/version, actor and privileges, entrypoint, expected boundary, actual path, source locations, narrow supported impact, counterevidence, reproduction status, remedy and remaining gaps.

Use repository-relative paths and synthetic data. Include commands and output only when inspected or actually executed, labeled accordingly. An expected result is not an observed trace. Leave affected release ranges, CVEs and CVSS unset when not established. Keep exploit details proportionate and private; never post sensitive reports in public issues or send them without explicit destination-specific authority.

## Tracking

Prepare a local Markdown issue draft or ledger when useful. Include stable finding ID, title, affected revision/locations, verdict, evidence, owner if established, remedy, validation acceptance criteria and status. Link duplicates while preserving their original IDs. A drafted issue is not a created ticket.

For requested external writeback, verify the exact destination and visibility, use the available authorized connector/CLI, and preserve the provider's returned URL/ID. Do not close a ticket merely because a patch exists: require the agreed verification. Never create duplicate tickets after an ambiguous provider response; check the original operation first.
