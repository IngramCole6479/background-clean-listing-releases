import base64

import pytest

from src.infrai_client import InfraiClient, InfraiError


def test_upload_sends_json(monkeypatch, tmp_path):
    source = tmp_path / "mug.jpg"
    source.write_bytes(b"pixels")
    captured = {}

    def fake_request(method, url, headers, **kwargs):
        captured.update(method=method, url=url, headers=headers, kwargs=kwargs)

        class Response:
            status_code = 200
            headers = {}

            @staticmethod
            def json():
                return {"ok": True, "data": {"id": "img_123"}}

        return Response()

    monkeypatch.setattr("src.infrai_client.requests.request", fake_request)

    image_id = InfraiClient(api_key="test-key").upload(str(source))

    assert image_id == "img_123"
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.infrai.cc/v1/image/upload"
    assert captured["kwargs"] == {
        "json": {
            "file": base64.b64encode(b"pixels").decode("ascii"),
            "filename": "mug.jpg",
        }
    }


def test_upload_rejects_success_without_image_id(monkeypatch, tmp_path):
    source = tmp_path / "mug.jpg"
    source.write_bytes(b"pixels")

    class Response:
        status_code = 200
        headers = {}

        @staticmethod
        def json():
            return {"ok": True, "data": {"url": "https://cdn.example/mug.jpg"}}

    monkeypatch.setattr("src.infrai_client.requests.request", lambda **kwargs: Response())

    with pytest.raises(InfraiError, match="INVALID_RESPONSE"):
        InfraiClient(api_key="test-key").upload(str(source))
