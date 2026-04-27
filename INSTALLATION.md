# Installation

## Prerequisites

- **uv** — manages the Python environment used by hooks.
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Node.js** (provides `npx`) — required by the puppeteer MCP server.
  ```
  # Linux arm64 example; pick the build matching your platform from https://nodejs.org/
  curl -LO https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-arm64.tar.xz
  mkdir -p ~/.local && tar -xf node-v22.11.0-linux-arm64.tar.xz -C ~/.local/
  ln -sf ~/.local/node-v22.11.0-linux-arm64/bin/{node,npm,npx} ~/.local/bin/
  ```

Make sure `~/.local/bin` is on your `PATH`.

## Set up the project

From the repo root:

```
uv sync
```

This creates `.venv/` with the dependencies the hooks rely on (e.g. `pydantic`). The hooks in `.claude/settings.json` invoke `$CLAUDE_PROJECT_DIR/.venv/bin/python3` directly, so no activation is needed.

## Verify

- Open the project in Claude Code — hooks should run without `ModuleNotFoundError`.
- Run `/mcp` — `puppeteer` should connect.
