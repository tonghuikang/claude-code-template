"""Typed Codex hook input models.

The codex hook runner sends different payload shapes across event types.
Using small dataclasses keeps parsing explicit while staying dependency-free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _coerce_text(value: Any) -> str:
    """Convert a payload field to a normalized string."""
    if not isinstance(value, str):
        return ""
    return value.strip()


def _coerce_bool(value: Any) -> bool:
    """Convert loosely-typed payload booleans to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _coerce_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


@dataclass(frozen=True)
class GenericHook:
    """Base hook model."""

    hook_event_name: str
    payload: dict[str, Any]

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "GenericHook":
        payload = _coerce_payload(payload)
        return GenericHook(
            hook_event_name=_coerce_text(payload.get("hook_event_name")),
            payload=payload,
        )


@dataclass(frozen=True)
class NotificationHook:
    """Model for Notification event payloads."""

    hook_event_name: str
    payload: dict[str, Any]
    message: str

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "NotificationHook":
        payload = _coerce_payload(payload)
        return NotificationHook(
            hook_event_name=_coerce_text(payload.get("hook_event_name")),
            payload=payload,
            message=_coerce_text(payload.get("message")),
        )


@dataclass(frozen=True)
class StopHook:
    """Model for Stop event payloads."""

    hook_event_name: str
    payload: dict[str, Any]
    last_assistant_message: str
    transcript_path: str
    stop_hook_active: bool

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "StopHook":
        payload = _coerce_payload(payload)
        return StopHook(
            hook_event_name=_coerce_text(payload.get("hook_event_name")),
            payload=payload,
            last_assistant_message=_coerce_text(payload.get("last_assistant_message")),
            transcript_path=_coerce_text(
                payload.get("transcript_path")
                or payload.get("transcript_file")
                or payload.get("session_transcript_path")
            ),
            stop_hook_active=_coerce_bool(payload.get("stop_hook_active")),
        )


def parse_hook_payload(payload: Any) -> GenericHook | NotificationHook | StopHook:
    """Parse raw payload into a typed model."""
    if not isinstance(payload, dict):
        return GenericHook.from_payload({})

    event_name = _coerce_text(payload.get("hook_event_name"))

    if event_name == "Stop":
        return StopHook.from_payload(payload)
    if event_name == "Notification":
        return NotificationHook.from_payload(payload)

    return GenericHook.from_payload(payload)
