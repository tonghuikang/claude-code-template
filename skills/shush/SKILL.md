---
name: shush
description: Stop the TTS notification voice. Kills `say` on macOS or cancels speech-dispatcher on Linux. Use when the spoken notification is still talking and the user wants it silenced.
disable-model-invocation: true
allowed-tools: Bash(killall:*) Bash(spd-say:*) Bash(uname:*)
---

# Shush

Silence the TTS notification voice started by `process_notification.py`.

Result: !`if [ "$(uname)" = "Darwin" ]; then killall say 2>/dev/null && echo "killed say" || echo "no say process"; else spd-say -C && echo "cancelled speech-dispatcher"; fi`

Just report the result above to the user. Do not run any further commands.
