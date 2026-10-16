# Bring your harness

ChatNoir ships a portable Agent Plugins 1.0 manifest, native Claude/Codex compatibility manifests and a self-contained Agent Skill. It does not require a vendor's security backend. “Portable” means the workflow and helpers are reusable; it does not mean every agent client has been tested.

| Host | Distribution | Evidence / limit |
|---|---|---|
| Codex | Repository marketplace, compatibility manifest, or `.agents/skills/chatnoir/` | Native CLI 0.157.0 model sessions loaded the plugin, found/reproduced all 3 known HTTP-fixture flaws, and produced a patch that passed an independent HTTP check. The installed skill also ran in the current desktop chat; the user manually confirmed it is installed and enabled in the Plugins page. The fresh installation flow and picker remain unverified because self-UI automation is blocked. |
| Claude Code | `.claude-plugin` marketplace/plugin or `.claude/skills/chatnoir/` | CLI 2.1.42 validated and discovered the native plugin. Initial and follow-up model requests failed authentication; valid model access was unavailable. Detection and remediation remain unverified. |
| Cursor | Native `.cursor-plugin` or portable manifest; project skill | CLI detection passed; its Auto provider blocked remediation. In IDE 3.24.12, project skill discovery, review and remediation passed with the visible default model, Cursor Grok 4.6 Medium; a separate HTTP probe passed all 8 checks. Native IDE marketplace/plugin installation remains unverified. |
| VS Code | Through a compatible agent extension | VS Code itself is an editor, not a universal skill/plugin host. No blanket extension compatibility claim. |
| Other Agent Skills hosts | Copy `skills/chatnoir/` into the host's supported skill root | Must support `SKILL.md`, relative references, file inspection and, for helpers, Python/terminal access. Not individually verified. |
| Any text-capable agent | Manually provide `SKILL.md` and relevant references | Manual instruction use only, not native plugin integration. Tool and execution limits still apply. |

## Skill-only installation

Run `python3 scripts/install.py --harness HOST --project EXISTING_PROJECT` from the clone. `codex` and `agents` choose `.agents/skills`; `claude` chooses `.claude/skills`; `cursor` chooses `.cursor/skills`. No global agent settings are changed. It refuses existing ChatNoir directories and linked destination directories. On an interrupted copy, inspect/remove only the incomplete new ChatNoir directory before retrying.

Restart the agent session, then ask it to use ChatNoir. To uninstall, remove only the copied `chatnoir` folder. Do not install several copies into directories your host scans together. Updating is deliberate: review the next release and replace your installation after preserving local customizations.

## Plugin development

```sh
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
claude --plugin-dir /absolute/path/to/ChatNoir
```

Codex CLI discovery can be checked without changing global configuration:

```sh
codex -c 'marketplaces.chatnoir-marketplace.source_type="local"' \
  -c 'marketplaces.chatnoir-marketplace.source="/absolute/path/to/ChatNoir"' \
  plugin list --marketplace chatnoir-marketplace --available --json
```

The repository marketplace uses `./` as its plugin path. To distribute the release ZIP, extract the full plugin directory, including dot-directories; copying just a manifest is insufficient. For security-sensitive projects, inspect a tagged release and pin your own installation to an exact commit.

See [native CLI evidence](harness-e2e.md) and [desktop/IDE evidence](desktop-e2e.md) for exact outcomes. In Cursor, plan mode may block Python helpers and runtime checks: keep the review static or explicitly authorize trusted commands in normal agent mode using the host's [project permission configuration](https://cursor.com/docs/cli/reference/permissions). Do not disable protections or force execution merely to make a test pass. ChatNoir reports provider/permission failures as gaps; it cannot override them.

## Upstream formats

Checked October 16, 2026: [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [Claude plugin manifests](https://code.claude.com/docs/en/plugins-reference), [Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Cursor Agent Skills](https://cursor.com/docs/skills), and [Cursor plugin reference](https://cursor.com/docs/reference/plugins). Public directory submission is a separate provider review process; this repository does not imply listing or endorsement.
