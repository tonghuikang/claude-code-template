# Claude Code Template

These are some rules you might want to impose on your coding agent:

- If asked to `ruff`, the coding agent should read a set of instructions
- The coding agent should not use Bash(grep), and should use the Grep tool instead
- The coding agent should not write `except Exception as e`
- After every edit, the coding agent will need to run a formatter

Traditionally, you would insert all these instructions into CLAUDE.md in some logical order.

However, I see many problems with solely depending on CLAUDE.md:

- CLAUDE.md should be maintained by one 'benevolent dictator', for reasons that would soon be obvious.
    The dictator will need to obtain the required trust and authority.
    The dictator will need to solicit change proposals to CLAUDE.md and reject many of them.
- Instructions are open to interpretation.
    For example, you have an instruction on avoiding exceptions.
    Does this mean to avoid all exceptions? Or some of them?
    The codebase is already full of exceptions - should they serve as a reference?
- Instructions cost money.
    It is possible to write a consistent guideline on exceptions, but it will take many words.
    The more comprehensive your guidelines, the more tokens you pay for on every single request.
    Every word in CLAUDE.md is overhead that you pay repeatedly.
- Instructions can break other instructions.
    The longer the instructions, the more likely there are instructions that are not followed.
    You do not want your colleagues to suspect that a recent addition to CLAUDE.md has caused Claude Code to not follow instructions that were previously followed.
- Instructions need to be tested.
    When you add an instruction to CLAUDE.md, you need to make sure you are not breaking other instructions.
    You can test either with an evaluation suite that you need to invest in, or you can try the new version of CLAUDE.md for a period of time.
    Even with testing, issues may arise.
- Models will improve.
    Your instructions to CLAUDE.md to fix the deficiencies of the model may be irrelevant with a model upgrade.
    For example, the current model may be using too many exceptions.
    You write strong instructions so that the model will use an appropriate level of exceptions.
    A new version of the model arrives, it may have an optimal taste on exceptions on an empty CLAUDE.md file.
    However, your old prompt now forces the model to unnecessarily avoid exceptions.
    These now redundant instructions harm the performance of your coding tool.


Therefore, instead of overloading CLAUDE.md with instructions that are not easily tested, you should deliver instructions at places where they are most relevant.

Claude Code hooks allow us to execute commands to deliver information at certain points of the agentic coding lifecycle.

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

**Example:** Enforces code quality standards
- Blocks broad `except Exception` statements, suggests specific exceptions
- Discourages `if TYPE_CHECKING:` patterns

### 4. PostToolUse (Bash)
Runs after Bash commands are executed.

**Example:** Detects chained commands with `&&`
- Suggests running commands individually instead of chaining them

### 5. Stop
Runs when Claude finishes responding.

**Example:** Enforces test-driven workflow after code changes
- Checks if Bash commands were run after Edit/Write operations
- Requires confirmation phrase "I have addressed every query from the user."

## Example Query

You can start Claude Code in this repository and provide the following query

```
Write a file in Python root containing `except Exception`
```

This demonstrates
- Edit hook giving comments on `except Exception`
- Stop hook validating that check were done after code changes
