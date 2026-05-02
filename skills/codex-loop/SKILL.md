---
name: codex-loop
description: Drive a plan.md file to completion using a codex worker/checker pair. The worker iteratively makes progress on unsatisfied requirements; the checker verifies completion against the plan and emits a sentinel when every requirement is met. Use when the user types `/codex-loop <plan.md>` or asks to run the codex loop on a plan file.
---

# codex-loop

Run the bundled script with the user's argument:

```bash
skills/codex-loop/codex-loop.sh "$1"
```

`$1` is the path to the plan markdown file. Forward it verbatim — the script resolves it to an absolute path internally.

## What it does

The script alternates two `codex exec` invocations until a sentinel line is emitted:

1. **Worker** — reads the plan, inspects repo state, picks an unsatisfied requirement, makes progress. Receives the previous checker's TODO list as a priority punch-list when present.
2. **Checker** — reads the plan, inspects repo state, does NOT modify files. Emits exactly `all requirements in <plan-basename>.md is fulfilled` when every requirement is satisfied, otherwise lists `TODO:` items per unsatisfied requirement.

The loop exits when the checker emits the sentinel as a whole line (trailing punctuation tolerated). `max_iters=0` means unlimited; edit the script to cap.

## Caveats

- Both worker and checker run with `codex exec --dangerously-bypass-approvals-and-sandbox` — they will read/write files and run shell commands without prompting. Only run this on plans you trust the worker to act on.
- The script does not push to remotes, but the worker may. If the plan needs to forbid pushes, state that in the plan body.
- Output is verbose. Run with stdout/stderr redirected to a log file when running in background.
