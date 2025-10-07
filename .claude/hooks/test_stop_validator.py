import json
import tempfile
from pathlib import Path

from stop_validator import validate_stop


def test_stop_validator_no_edits():
    """Test that stop_validator returns no issues when no edits are made"""
    transcript_data = {
        "type": "assistant",
        "message": {
            "content": [{"type": "text", "text": "Some response without edits"}]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(transcript_data) + "\n")
        transcript_path = f.name

    try:
        issues = validate_stop(transcript_path)
        assert issues == []
    finally:
        Path(transcript_path).unlink()


def test_stop_validator_with_edits_and_confirmation():
    """Test that stop_validator returns no issues when edits are made with bash and confirmation phrase"""
    transcript_data = {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "Edit",
                    "input": {"old_string": "foo", "new_string": "bar"},
                },
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": "pytest"},
                },
                {
                    "type": "tool_use",
                    "name": "TodoWrite",
                    "input": {
                        "todos": [
                            {
                                "content": "Test task",
                                "status": "completed",
                                "activeForm": "Testing task",
                            }
                        ]
                    },
                },
                {
                    "type": "text",
                    "text": "I have addressed every query from the user.",
                },
            ]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(transcript_data) + "\n")
        transcript_path = f.name

    try:
        issues = validate_stop(transcript_path)
        assert issues == []
    finally:
        Path(transcript_path).unlink()


def test_stop_validator_with_edits_no_confirmation():
    """Test that stop_validator returns issues when edits are made but confirmation phrase is missing"""
    transcript_data = {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "Edit",
                    "input": {"old_string": "foo", "new_string": "bar"},
                },
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": "pytest"},
                },
                {"type": "text", "text": "Some other text without the confirmation"},
            ]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(transcript_data) + "\n")
        transcript_path = f.name

    try:
        issues = validate_stop(transcript_path)
        assert len(issues) > 0
        assert "Review your work" in issues[0]
    finally:
        Path(transcript_path).unlink()
