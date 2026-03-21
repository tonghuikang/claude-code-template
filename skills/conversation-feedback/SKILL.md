---
name: conversation-feedback
description: Analyze a conversation to identify issues and suggest improvements. Use if reflecting on the current conversation.
---

# Conversation Feedback

Analyze the current coding session to identify what went wrong and what can be improved.

Example queries:
- /conversation-feedback


## Workflow

### Step 1: Obtain the conversation

If the conversation is compacted, you will figure out where the conversations are
- For Claude Code, you should be informed of the transcript path after compaction.
- For Codex, the conversation is saved at `~/.codex/sessions/` (or `$CODEX_HOME/sessions/`).


### Step 2: Understand the task

Understand what the user is actually asking for.

For each follow-up ask from the user, identify whether it is:
- A new instruction from the user
- A correction of the model's mistake
- A clarification the model should have inferred
- An approval or rejection of the model's output


### Step 3: Understand the issues

These are considered issues with the conversation

- The user pointing out a mistake with the agent's work
- The agent is executing bash commands where it could have executed a much simpler bash command
- The agent is forced to read a lot of instructions that are irrelevant
- The agent going in circles (repeated similar attempts without progress)
- The agent not following skill or CLAUDE.md instructions
- The agent is not testing their own work

These are not considered issues in the conversation

- The model doing the necessary research efficiently
- User requesting a different approach in the middle
- The irrelevant instructions that the agent is reading are short


Every issue MUST include concrete evidence from the conversation (e.g., quote the model's message, cite the tool call, reference the instruction that was violated). Do not report an issue without verifying it against the conversation history first.

If there are no issues with the conversation, say so and write a note.


### Step 4: Understand the causes

When a conversation is inefficient, something must be at fault.

The fault could be in
- user instruction
- built-in instruction (e.g. AI tooling system instructions)
- global instructions (e.g. CLAUDE.md, AGENTS.md)
- the skill instruction
- the code
- the model


### Step 5: Propose improvements

These are places where improvements can be made

- User
  - The user could interact with the model better by learning certain specific concepts and vocabulary.
- Global instructions
  - If certain global instruction do not apply to your use case, do point that out.
  - Avoid suggesting adding instruction that do not benefit all tasks to global instructions.
- Skills
  - The skill could be clearer on what the pitfalls are, and document the pitfalls to avoid.
  - Mention exactly which skill could be improved.
- Hooks
  - Instructions from the hooks could be improved.
- Code
  - The pre-existing code could have been better written to avoid footguns.

The model is NOT a valid suggested improvement.
- Even if the model is the main cause of the inefficiency, still suggest how other improvements to instructions could be made.


### Step 6: Produce a report

Produce a report. The report should end with ONE markdown table with the following columns
- Issue
- Where to fix
- What to fix
