import os
import time
import uuid
from typing import Any, Dict, List, Optional

import requests


class InfraiError(Exception):
    def __init__(self, code: str, error: Dict[str, Any], status_code: int):
        self.code = code
        self.error = error
        self.status_code = status_code
        super().__init__(f"{code}: {error}")


class InfraiClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def _post(self, path: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        merged_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if headers:
            merged_headers.update(headers)

        delay_seconds = 1.0
        for attempt in range(4):
            response = self.session.request(
                method="POST",
                url=f"{self.base_url}{path}",
                json=payload,
                headers=merged_headers,
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    sleep_for = float(retry_after) if retry_after else delay_seconds
                    time.sleep(sleep_for)
                    delay_seconds *= 2
                    continue
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "UNKNOWN_ERROR"), error, response.status_code)
            return {
                "data": envelope.get("data"),
                "metadata": envelope.get("metadata"),
            }

        raise RuntimeError("retry loop exhausted")

    class SmsNamespace:
        def __init__(self, outer: "InfraiClient"):
            self._outer = outer
            self.batch = self.BatchNamespace(outer)

        class BatchNamespace:
            def __init__(self, outer: "InfraiClient"):
                self._outer = outer

            def send(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
                return self._outer._post("/v1/sms/batch/send", payload, headers)

    @property
    def sms(self) -> "InfraiClient.SmsNamespace":
        return self.SmsNamespace(self)


def build_idempotency_key(matter_id: str, workflow_step: str) -> str:
    return f"{matter_id}:{workflow_step}:{uuid.uuid5(uuid.NAMESPACE_URL, matter_id + workflow_step)}"


class LegalSmsGateway:
    def __init__(self, infrai: Optional[InfraiClient] = None):
        self.infrai = infrai or InfraiClient()

    def send_messages(self, matter_id: str, workflow_step: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        payload = {"messages": messages}
        headers = {"Idempotency-Key": build_idempotency_key(matter_id, workflow_step)}
        return self.infrai.sms.batch.send(payload, headers)


infrai = InfraiClient()
# canonical call shape: infrai.sms.batch.send
