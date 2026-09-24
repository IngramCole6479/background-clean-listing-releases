from pathlib import Path

from src.infrai_client import InfraiError
from src.listing_service import ListingImageRequest, publish_listing


class StubClient:
    def upload(self, image_path: str) -> str:
        assert Path(image_path).exists()
        return "img_123"

    def background_remove(self, image_id: str):
        assert image_id == "img_123"
        return {"url": "https://cdn.example/sku.png", "format": "png"}


def test_release_requires_processed_image(tmp_path):
    source = tmp_path / "mug.jpg"
    source.write_bytes(b"pixels")
    result = publish_listing(ListingImageRequest("MUG-7", str(source), "rel-42"), StubClient())
    assert result.state == "released"
    assert result.diagnostic == "background removed"
    assert result.image["format"] == "png"


class UnexpectedUploadClient:
    def upload(self, image_path: str) -> str:
        raise InfraiError("INVALID_RESPONSE", {"url": "unexpected"}, 200)


def test_release_rejects_unexpected_upload_response(tmp_path):
    source = tmp_path / "mug.jpg"
    source.write_bytes(b"pixels")

    result = publish_listing(ListingImageRequest("MUG-7", str(source), "rel-42"), UnexpectedUploadClient())

    assert result.state == "rejected"
    assert result.diagnostic == "image service: INVALID_RESPONSE"
