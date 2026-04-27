---
name: shush
description: Stop the TTS notification voice. Kills `say` on macOS or the Kokoro notification subprocess on Linux. Use when the spoken notification is still talking and the user wants it silenced.
disable-model-invocation: true
allowed-tools: Bash(killall:*) Bash(pkill:*) Bash(uname:*)
---

# Shush

Silence the TTS notification voice started by `process_notification.py`.

Result: !`if [ "$(uname)" = "Darwin" ]; then killall say 2>/dev/null && echo "killed say" || echo "no say process"; else pkill -f notify_kokoro.py 2>/dev/null; pkill -x aplay 2>/dev/null; echo "silenced kokoro/aplay"; fi`

Just report the result above to the user. Do not run any further commands.
