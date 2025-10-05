# Claude Code Template

These are some rules you might want to impose on your coding agent:

- If asked to `ruff`, you should read a set of instructions
- Do not use Bash(grep), use the Grep tool instead
- Do not write `except Exception as e`
- After every edit, you will need to run a formatter

Traditionally, you would insert all these instructions into CLAUDE.md in some logical order.

However, I see many problems with solely depending on CLAUDE.md:

- CLAUDE.md needs to be maintained by one 'benevolent dictator'.
    The dictator will need to obtain the trust and authority from the organization.
    The dictator will need to solicit change proposals to CLAUDE.md and reject many of them.
    The dictator will need to be aware of contradictions within the instructions.
- The longer the instructions, the more likely there are instructions that are not followed.
    You do not want your colleagues to suspect that a recent addition to CLAUDE.md has caused Claude Code to not follow instructions that were previously followed.
- Testing is needed, and it takes time and is incomplete.
    When you add an instruction to CLAUDE.md, you need to make sure you are not breaking other instructions.
    You can test either with an evaluation suite that you need to invest in, or you can try the new version of CLAUDE.md for a period of time.
    Even with testing, issues may arise.
- Models will improve.
    Many instructions you add to CLAUDE.md to fix the deficiencies of the model may be irrelevant with a model upgrade.
    In fact, these redundant instructions might harm the performance of your coding tool.


Therefore, instead of overloading CLAUDE.md with instructions that are not easily tested, you should deliver instructions at places where they are most relevant.

Claude Code hooks allow us to execute commands at certain points of the agentic coding lifecycle.

This is a template for you to easily configure Claude Code hooks.


## Available Hooks

This repository demonstrates hook types that execute at different points in the agentic lifecycle:

### 1. UserPromptSubmit
Runs when the user submits a prompt.

**Example:** Intercepts "ruff" keyword to inject CLAUDE.md instructions
- When user types "ruff", the hook adds context-specific formatting instructions

### 2. PreToolUse (Bash)
Runs before Bash commands are executed.

**Examples:**
- Blocks `Bash(grep)` commands, redirects to Grep tool
- Blocks `python` commands, redirects to `uv run python`

### 3. PostToolUse (Edit/Write)
Runs after Edit or Write operations.

**Example:** Validates content
- Catches `except Exception`, `TYPE_CHECKING`

### 4. PostToolUse (Bash)
Runs after Bash commands are executed.

**Example:** Validates commands after execution

### 5. Stop
Runs when Claude finishes responding.

**Example:** Validates transcript for required actions
- Checks if necessary follow-up steps were completed

## Example Query

```
move the "Bash(grep)" check from pre bash to post bash
```

This demonstrates the Stop hook validating that tests were run after code changes.
