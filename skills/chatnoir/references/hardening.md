# Structural hardening proposals

Start with supplied findings and inspected code. Propose architecture work only if evidence shows a common structural cause: duplicated authorization, repeated unsafe conversion, excessive ambient privilege or a shared enforcement gap. Independent flaws may be better addressed by local fixes; say so.

Define the invariant, affected surfaces, compatibility obligations and budget. Compare the smallest local remedy with materially different structural options. For each, explain how enforcement changes, what remains exposed, engineering effort, performance/resource uncertainty, operational burden, migration and rollback. Label source-derived conclusions, forecasts and measured results distinctly. Never invent performance gains or security percentages.

Map each finding to addressed, mitigated, unaffected or unknown for each option. Keep tactical protections during migration. Use a diagram only when it makes control ownership clearer. Recommend the smallest proportionate option and state what evidence would change it. A proposal does not fix a vulnerability; wait for implementation authority, then verify the original paths against the resulting code.
