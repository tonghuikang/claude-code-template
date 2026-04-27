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
- **Skills** — bundled skills (`check-deliverables`, `conversation-feedback`, `shush`)
- **Puppeteer MCP** — preconfigured `.mcp.json` for browser automation
