"""IBVAP intrusion event engine module."""

from ai.events.engine import IntrusionEventEngine, encode_frame_to_base64
from ai.events.schemas import EventPayload, EventType, Severity
from ai.events.dispatcher import EventDispatcher, DispatchResult

__all__ = [
    "IntrusionEventEngine",
    "EventPayload",
    "EventType",
    "Severity",
    "encode_frame_to_base64",
    "EventDispatcher",
    "DispatchResult",
]
