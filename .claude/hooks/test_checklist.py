import json
import sys
import tempfile
from pathlib import Path
from unittest import mock


def test_checklist_no_edits():
    """Test that checklist exits successfully when no edits are made"""
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
        input_data = {"transcript_path": transcript_path}
        with mock.patch("sys.stdin"):
            with mock.patch("json.load", return_value=input_data):
                # Run the checklist script directly
                import subprocess

                result = subprocess.run(
                    [sys.executable, ".claude/checklist.py"],
                    input=json.dumps(input_data),
                    capture_output=True,
                    text=True,
                )
                # Should exit 0 or complete without error when no edits
                assert result.returncode in [0, None]
    finally:
        Path(transcript_path).unlink()


def test_checklist_with_edits_and_confirmation():
    """Test that checklist exits successfully when edits are made and confirmation phrase is present"""
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
        input_data = {"transcript_path": transcript_path}
        import subprocess

        result = subprocess.run(
            [sys.executable, ".claude/checklist.py"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
    finally:
        Path(transcript_path).unlink()


def test_checklist_with_edits_no_confirmation():
    """Test that checklist exits with error when edits are made but confirmation phrase is missing"""
    transcript_data = {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "Edit",
                    "input": {"old_string": "foo", "new_string": "bar"},
                },
                {"type": "text", "text": "Some other text without the confirmation"},
            ]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(transcript_data) + "\n")
        transcript_path = f.name

    try:
        input_data = {"transcript_path": transcript_path}
        import subprocess

        result = subprocess.run(
            [sys.executable, ".claude/checklist.py"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
    finally:
        Path(transcript_path).unlink()
