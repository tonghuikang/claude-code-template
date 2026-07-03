# Claude Code Template

A template for configuring Claude Code hooks to deliver instructions at the most relevant points in the agentic coding lifecycle, instead of overloading CLAUDE.md.

This template covers:

- **UserPromptSubmit** — inject context based on the user's prompt
- **PreToolUse (Bash)** — gate or rewrite shell commands before they run
- **PreToolUse (WebFetch)** — gate web fetches before they run
- **PostToolUse (Bash)** — react to command output (e.g. flag chained `&&` commands)
- **PostToolUse (Edit/Write)** — enforce code-quality rules on edits
- **Notification** — handle Claude Code notifications
- **Stop** — validate the agent's response before it's finalized
- **Skills** — bundled skill (`kaggle`), shared via the `skills/` directory
- **Puppeteer MCP** — preconfigured `.mcp.json` for browser automation

## Layout

The hook business logic lives in `hooks/` at the repository root and is shared
by both agents. `.claude/hooks/` and `.codex/hooks/` contain only thin
wrappers: each parses its agent's hook payload and dispatches to the shared
validators in `hooks/`.

- `hooks/` — validators, notification TTS, and their tests (dependency-free
  where Codex's system python needs them)
- `.claude/hooks/` — Claude Code dispatcher (`process_hooks.py`) and dataclass
  payload models, wired up in `.claude/settings.json`
- `.codex/hooks/` — Codex dispatcher (`process_hooks.py`) and dataclass
  payload models, wired up in `.codex/hooks.json`
- `skills/` — shared skills; `.claude/skills` and `.codex/skills` are symlinks
  to this directory
