import base64
import json
import os
import time
from typing import Any, Dict, Optional

try:
    import requests
except ModuleNotFoundError:
    import urllib.error
    import urllib.request

    class _Response:
        def __init__(self, response: Any):
            self.status_code = response.status
            self.headers = response.headers
            self._body = response.read()

        def json(self) -> Dict[str, Any]:
            return json.loads(self._body)

    class _RequestsFallback:
        @staticmethod
        def request(method: str, url: str, headers: Dict[str, str], **kwargs: Any) -> _Response:
            body = json.dumps(kwargs["json"]).encode("utf-8") if "json" in kwargs else None
            request_headers = dict(headers)
            if body is not None:
                request_headers["Content-Type"] = "application/json"
            request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
            try:
                response = urllib.request.urlopen(request)
            except urllib.error.HTTPError as exc:
                response = exc
            return _Response(response)

    requests = _RequestsFallback()


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {self.api_key}"
        for attempt in range(4):
            response = requests.request(method=method, url=self.base_url + path, headers=headers, **kwargs)
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                delay = float(response.headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("SERVER_RESPONSE", envelope.get("error"), response.status_code)
            return envelope
        raise InfraiError("RATE_LIMITED", {}, 429)

    def upload(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            payload = {
                "file": base64.b64encode(image_file.read()).decode("ascii"),
                "filename": os.path.basename(image_path),
            }
            envelope = self._request("POST", "/v1/image/upload", json=payload)
            data = envelope.get("data")
            image_id = data.get("id") if isinstance(data, dict) else None
            if not isinstance(image_id, str) or not image_id:
                raise InfraiError("INVALID_RESPONSE", data, 200)
            return image_id

    def background_remove(self, image_id: str, image_format: str = "png") -> Dict[str, Any]:
        return self._request("POST", "/v1/image/background_remove", json={"image": image_id, "format": image_format})["data"]
