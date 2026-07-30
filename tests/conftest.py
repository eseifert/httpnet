import json
from typing import Any

import pytest
import requests

from httpnet._core import Client


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, Any]:
        return self._payload


class RecordingSession:
    """Stands in for ``requests.Session`` and records the calls made to it."""

    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.calls: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []

    def post(self, url: str, data: str, timeout: Any) -> FakeResponse:
        self.calls.append({'url': url, 'body': json.loads(data), 'timeout': timeout})
        payload = self.responses.pop(0) if self.responses else {'status': 'success', 'response': {}}
        return FakeResponse(payload)


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch) -> RecordingSession:
    """Makes every ``Client`` created in a test use a recording session."""
    recording_session = RecordingSession()
    monkeypatch.setattr(requests, 'Session', lambda: recording_session)
    return recording_session


@pytest.fixture
def client(session: RecordingSession) -> Client:
    return Client(auth_token='token')
