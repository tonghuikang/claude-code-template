#!/usr/bin/env bash
# codex-loop: drive a plan to completion with a worker/checker pair.
#
# Usage: codex-loop <plan.md>
#
# Tunables — edit in place:
#   sentinel    exact line the checker must emit to stop the loop
#   max_iters   hard cap on iterations (0 = unlimited)
#   model       model passed to both agents ("" = codex default)

set -uo pipefail

main() {
    local sentinel_template='all requirements in <plan> is fulfilled'
    local max_iters=0
    local model=''

    local plan="${1:-}"
    if [[ -z "$plan" ]]; then
        echo "usage: codex-loop <plan.md>" >&2
        return 2
    fi
    if [[ ! -f "$plan" ]]; then
        echo "codex-loop: plan file not found: $plan" >&2
        return 2
    fi

    # Portable absolute path (macOS lacks GNU realpath by default).
    local plan_abs
    plan_abs="$(cd "$(dirname "$plan")" && pwd)/$(basename "$plan")"

    # Substitute <plan> in the sentinel with the actual plan basename so
    # the checker can't trivially emit it while paraphrasing the plan.
    local plan_name
    plan_name="$(basename "$plan_abs")"
    local sentinel="${sentinel_template/<plan>/$plan_name}"

    local model_args=()
    if [[ -n "$model" ]]; then
        model_args=(-m "$model")
    fi

    # If a sudo password is loaded in the env, let codex's child shells
    # inherit it. Mention to the worker that it's available — only if
    # something actually needs root. Let codex pick the invocation style.
    local sudo_args=()
    local sudo_hint=''
    if [[ -n "${SUDO_PASSWORD:-}" ]]; then
        sudo_args=(-c shell_environment_policy.inherit=all)
        sudo_hint=" The env var \$SUDO_PASSWORD (value: $SUDO_PASSWORD) is available if — and only if — a step actually requires root. Use it however you like; do not invoke sudo unnecessarily."
    fi

    local verdict_file
    verdict_file="$(mktemp)" || return 1
    # shellcheck disable=SC2064
    trap "rm -f '$verdict_file'" RETURN

    local prior_verdict=''
    local i=0
    while true; do
        i=$((i + 1))
        if (( max_iters > 0 && i > max_iters )); then
            echo "=== codex-loop: hit max_iters=$max_iters, giving up ===" >&2
            return 1
        fi

        local worker_prompt="Read the plan at $plan_abs. Inspect the current repository state to see what is already done. Then make as much concrete progress as you can on any unsatisfied requirement. Do not stop until you have finished a meaningful unit of work or are blocked. Do not ask questions; make reasonable assumptions.${sudo_hint}"
        if [[ -n "$prior_verdict" ]]; then
            worker_prompt="${worker_prompt}

The previous checker iteration produced the following TODO list of unsatisfied requirements. Treat this as your priority punch list for this iteration — resolve these items first before doing anything else, and do not redo work that the checker did not flag:

${prior_verdict}"
        fi

        echo "=== codex-loop iter $i: worker on $plan_abs ===" >&2
        codex exec --dangerously-bypass-approvals-and-sandbox ${model_args[@]+"${model_args[@]}"} ${sudo_args[@]+"${sudo_args[@]}"} "$worker_prompt"

        echo "=== codex-loop iter $i: checker ===" >&2
        : > "$verdict_file"
        codex exec --dangerously-bypass-approvals-and-sandbox ${model_args[@]+"${model_args[@]}"} \
            --output-last-message "$verdict_file" \
            "Read the plan at $plan_abs and inspect the current repository state. Do NOT modify any files. Decide whether every single requirement in the plan is fully satisfied right now. If yes, respond with EXACTLY this one line and nothing else: ${sentinel}. If not, list each unsatisfied requirement on its own line, prefixed with 'TODO: '."

        # Whole-line match, tolerant of trailing whitespace/punctuation
        # (the checker LLM tends to append a period). Still strict enough
        # that the sentinel embedded inside a longer sentence won't match.
        if awk -v target="$sentinel" '{
                line=$0
                sub(/[[:space:][:punct:]]+$/, "", line)
                if (line == target) { ok=1; exit }
            } END { exit !ok }' "$verdict_file" 2>/dev/null; then
            echo "=== codex-loop: done after $i iter(s) ===" >&2
            cat "$verdict_file"
            return 0
        fi

        echo "=== codex-loop iter $i: not done yet, looping ===" >&2
        if [[ -s "$verdict_file" ]]; then
            sed 's/^/    /' "$verdict_file" >&2
            prior_verdict="$(cat "$verdict_file")"
        else
            prior_verdict=''
        fi
    done
}

main "$@"
