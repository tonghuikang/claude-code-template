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
checks in `hooks/`.

- `hooks/` — per-event checks, notification TTS, and their tests (dependency-free
  where Codex's system python needs them)
- `.claude/hooks/` — Claude Code dispatcher (`process_hooks.py`) and dataclass
  payload models, wired up in `.claude/settings.json`
- `.codex/hooks/` — Codex dispatcher (`process_hooks.py`) and dataclass
  payload models, wired up in `.codex/hooks.json`
- `skills/` — shared skills; `.claude/skills` and `.codex/skills` are symlinks
  to this directory

## Notifications

Notification and Stop events are spoken aloud via Kokoro TTS
(`hooks/notify_kokoro.py`), played through `afplay` on macOS and
`pw-play`/`aplay` on Linux. Loading torch and the Kokoro model costs ~5s, so
the first notification spawns a daemon that keeps the model in memory and
listens on a Unix socket; later notifications forward their message to it in
under 0.2s. The daemon exits after 30 minutes without a message to release
its ~500MB of memory.

To silence a notification mid-speech, add a shush alias to your shell rc
(killing only the player leaves the daemon warm):

```zsh
alias ss='pkill afplay; pkill pw-play; pkill aplay'
```

To mute narration entirely for an hour (e.g. before a call), add `ssn`. It
kills any in-progress playback and writes the current time to
`~/.narrate_mute`; `speak()` in `hooks/notification.py` checks that file and
stays quiet until the hour is up (missing/stale file means narrate):

```zsh
alias ssn='pkill afplay; pkill pw-play; pkill aplay; date +%s > ~/.narrate_mute && echo "narration muted until $(date -v+1H)"'
```

To lift the mute early, add `ssy`. It deletes `~/.narrate_mute`, which is the
same as letting the hour expire:

```zsh
alias ssy='rm -f ~/.narrate_mute && echo "narration unmuted"'
```
