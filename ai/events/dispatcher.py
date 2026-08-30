"""
M1 Backend Event Dispatcher for IBVAP AI Engine.

Handles secure authentication, JWT token caching/refresh, EventPayload -> EventCreate mapping,
bounded retry policies, HTTP 409 Conflict idempotency, and asynchronous/synchronous transmission
of detected intrusion events to the M1 FastAPI backend.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
import httpx

from ai.core.config import ai_settings
from ai.events.schemas import EventPayload

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    """Represents the outcome of an event dispatch attempt."""

    success: bool
    event_identifier: str
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    attempts: int = 1


class EventDispatcher:
    """
    HTTP client responsible for dispatching intrusion events to M1 FastAPI backend.
    """

    def __init__(
        self,
        backend_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self.backend_url = (backend_url or ai_settings.BACKEND_URL).rstrip("/")
        self.username = username or ai_settings.USERNAME
        self.password = password or ai_settings.PASSWORD
        self.timeout = timeout if timeout is not None else ai_settings.DISPATCH_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else ai_settings.DISPATCH_RETRIES

        self._access_token: Optional[str] = None
        self._token_acquired_at: float = 0.0

    def is_authenticated(self) -> bool:
        """Check if dispatcher currently holds an access token."""
        return self._access_token is not None

    def clear_token(self) -> None:
        """Clear cached access token."""
        self._access_token = None
        self._token_acquired_at = 0.0

    def login(self, client: Optional[httpx.Client] = None) -> str:
        """
        Authenticate with backend via POST /api/v1/auth/login and cache the JWT token.
        """
        url = f"{self.backend_url}/api/v1/auth/login"
        payload = {"username_or_email": self.username, "password": self.password}

        logger.info(f"Authenticating AI EventDispatcher with backend at {self.backend_url}...")


        should_close = False
        if client is None:
            client = httpx.Client(timeout=self.timeout)
            should_close = True

        try:
            response = client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Authentication failed: HTTP {response.status_code}")
                raise RuntimeError(f"Failed to authenticate with backend: HTTP {response.status_code}")

            data = response.json()
            token = data.get("access_token") or data.get("mfa_token")
            if not token:
                raise ValueError("Backend login response missing 'access_token' or 'mfa_token'")

            self._access_token = token
            self._token_acquired_at = time.time()
            logger.info("AI EventDispatcher authenticated successfully (JWT token cached).")
            return token

        finally:
            if should_close:
                client.close()

    def get_auth_headers(self, client: Optional[httpx.Client] = None) -> Dict[str, str]:
        """
        Return authorization headers with Bearer token, acquiring token if necessary.
        """
        if not self._access_token:
            self.login(client=client)
        return {"Authorization": f"Bearer {self._access_token}"}

    def map_payload_to_event_create(
        self,
        payload: EventPayload,
        camera_id: str,
        zone_id: Optional[str] = None,
        event_identifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transforms internal EventPayload into exact M1 backend EventCreate JSON schema.
        """
        # Generate or reuse deterministic event identifier
        if not event_identifier:
            ts_str = payload.timestamp
            try:
                dt = datetime.fromisoformat(ts_str)
                ts_ms = int(dt.timestamp() * 1000)
            except Exception:
                ts_ms = int(time.time() * 1000)
            clean_cam = camera_id.replace("-", "")[:8]
            event_identifier = f"evt-{clean_cam}-{payload.track_id}-{ts_ms}"

        # Bounding box mapping: [x1, y1, x2, y2] -> {"x1": ..., "y1": ..., "x2": ..., "y2": ...}
        bbox = payload.bbox
        bbox_dict = None
        pos_dict = None
        if bbox and len(bbox) == 4:
            x1, y1, x2, y2 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            bbox_dict = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            pos_dict = {"x": (x1 + x2) / 2.0, "y": y2}

        # Timestamp normalization to ISO-8601 UTC
        ts_val = payload.timestamp
        try:
            dt = datetime.fromisoformat(ts_val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            iso_timestamp = dt.isoformat()
        except Exception:
            iso_timestamp = datetime.now(timezone.utc).isoformat()

        event_create_dict: Dict[str, Any] = {
            "event_identifier": event_identifier,
            "event_type": payload.event_type,
            "camera_id": camera_id,
            "zone_id": zone_id or payload.zone_id,
            "track_id": payload.track_id,
            "timestamp": iso_timestamp,
            "severity": payload.severity,
            "status": "NEW",
            "bounding_box": bbox_dict,
            "position": pos_dict,
            "metadata": {
                "class_name": payload.class_name,
                "confidence": round(payload.confidence, 4),
            },
        }

        return event_create_dict

    def validate_camera_and_zone(
        self,
        camera_id: str,
        zone_id: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Pre-flight check: Verifies that configured camera and zone exist on M1 backend
        and that the zone is assigned to the specified camera.
        Returns: (is_valid: bool, camera_data: dict, zone_data: dict)
        """
        should_close = False
        if client is None:
            client = httpx.Client(timeout=self.timeout)
            should_close = True

        try:
            headers = self.get_auth_headers(client=client)

            # 1. Fetch camera
            cam_url = f"{self.backend_url}/api/v1/cameras/{camera_id}"
            cam_resp = client.get(cam_url, headers=headers)
            if cam_resp.status_code != 200:
                logger.error(f"Pre-flight validation failed: Camera '{camera_id}' not found (HTTP {cam_resp.status_code}).")
                return False, None, None
            camera_data = cam_resp.json()

            # 2. Fetch zone if provided
            zone_data = None
            if zone_id:
                zone_url = f"{self.backend_url}/api/v1/zones/{zone_id}"
                zone_resp = client.get(zone_url, headers=headers)
                if zone_resp.status_code != 200:
                    logger.error(f"Pre-flight validation failed: Zone '{zone_id}' not found (HTTP {zone_resp.status_code}).")
                    return False, camera_data, None

                zone_data = zone_resp.json()
                if zone_data.get("camera_id") != camera_id:
                    logger.error(
                        f"Pre-flight validation failed: Zone '{zone_id}' belongs to camera '{zone_data.get('camera_id')}', not '{camera_id}'."
                    )
                    return False, camera_data, zone_data

            logger.info(f"Pre-flight validation successful for camera '{camera_id}' and zone '{zone_id}'.")
            return True, camera_data, zone_data

        except Exception as e:
            logger.warning(f"Could not complete pre-flight validation against backend: {e}")
            return False, None, None
        finally:
            if should_close:
                client.close()

    def dispatch_event(
        self,
        payload: EventPayload,
        camera_id: str,
        zone_id: Optional[str] = None,
        event_identifier: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ) -> DispatchResult:
        """
        Synchronously dispatch an event payload to M1 backend with bounded retry and idempotency.
        """
        event_body = self.map_payload_to_event_create(
            payload=payload,
            camera_id=camera_id,
            zone_id=zone_id,
            event_identifier=event_identifier,
        )
        evt_id = event_body["event_identifier"]
        url = f"{self.backend_url}/api/v1/events"

        should_close = False
        if client is None:
            client = httpx.Client(timeout=self.timeout)
            should_close = True

        attempts = 0
        last_error = None
        status_code = None

        try:
            while attempts < self.max_retries:
                attempts += 1
                try:
                    headers = self.get_auth_headers(client=client)
                    response = client.post(url, json=event_body, headers=headers)
                    status_code = response.status_code

                    # HTTP 201: Successfully created
                    if status_code == 201:
                        resp_json = response.json()
                        logger.info(
                            f"Dispatched intrusion event '{evt_id}' -> M1 Event ID: {resp_json.get('id')}, Alert ID: {resp_json.get('alert_id')}"
                        )
                        return DispatchResult(
                            success=True,
                            event_identifier=evt_id,
                            status_code=201,
                            response_data=resp_json,
                            attempts=attempts,
                        )

                    # HTTP 409: Conflict (Idempotent success - already recorded)
                    elif status_code == 409:
                        logger.warning(f"Event '{evt_id}' already recorded in M1 backend (HTTP 409 Conflict - Idempotent).")
                        return DispatchResult(
                            success=True,
                            event_identifier=evt_id,
                            status_code=409,
                            response_data={"detail": "Event already recorded"},
                            attempts=attempts,
                        )

                    # HTTP 401: Unauthorized -> Token expired, re-authenticate once
                    elif status_code == 401:
                        logger.warning(f"JWT expired during dispatch attempt {attempts}. Re-authenticating...")
                        self.clear_token()
                        self.login(client=client)
                        continue

                    # Other client errors (4xx): Do not retry indefinitely
                    elif 400 <= status_code < 500:
                        err_msg = f"Client error from backend: HTTP {status_code} - {response.text}"
                        logger.error(f"Event dispatch rejected: {err_msg}")
                        return DispatchResult(
                            success=False,
                            event_identifier=evt_id,
                            status_code=status_code,
                            error_message=err_msg,
                            attempts=attempts,
                        )

                    # Server errors (5xx): Retry
                    else:
                        last_error = f"Server returned HTTP {status_code}"
                        logger.warning(f"Dispatch attempt {attempts} failed with {last_error}. Retrying...")

                except httpx.RequestError as req_err:
                    last_error = str(req_err)
                    logger.warning(f"Dispatch attempt {attempts} network error: {last_error}. Retrying...")

                if attempts < self.max_retries:
                    time.sleep(0.2 * (2 ** (attempts - 1)))

            err_summary = f"Failed to dispatch event '{evt_id}' after {attempts} attempts. Last error: {last_error}"
            logger.error(err_summary)
            return DispatchResult(
                success=False,
                event_identifier=evt_id,
                status_code=status_code,
                error_message=err_summary,
                attempts=attempts,
            )

        finally:
            if should_close:
                client.close()
