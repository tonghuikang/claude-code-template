"""Tests for check_stop.py."""

import json

from check_stop import TEST_PHRASE, check_stop


def test_check_stop_flags_test_phrase_in_message():
    issues = check_stop("", f"All done. {TEST_PHRASE}.")
    assert len(issues) == 1
    assert "test" in issues[0].lower()


def test_check_stop_is_case_insensitive():
    assert len(check_stop("", TEST_PHRASE.upper())) == 1


def test_check_stop_allows_normal_message():
    assert check_stop("", "All done, tests pass.") == []


def test_check_stop_allows_empty():
    assert check_stop("", "") == []


def test_check_stop_reads_transcript_when_message_missing(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    records = [
        {"message": {"role": "user", "content": "please run the tests"}},
        {"message": {"role": "assistant", "content": f"ok. {TEST_PHRASE}"}},
    ]
    transcript.write_text("\n".join(json.dumps(r) for r in records))
    assert len(check_stop(str(transcript), "")) == 1


def test_check_stop_transcript_last_message_wins(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    records = [
        {"message": {"role": "assistant", "content": TEST_PHRASE}},
        {"message": {"role": "assistant", "content": "a clean final reply"}},
    ]
    transcript.write_text("\n".join(json.dumps(r) for r in records))
    assert check_stop(str(transcript), "") == []
