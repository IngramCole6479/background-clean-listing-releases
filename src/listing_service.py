from dataclasses import dataclass
from typing import Any, Dict

from .infrai_client import InfraiClient, InfraiError


@dataclass(frozen=True)
class ListingImageRequest:
    sku: str
    source_path: str
    release_id: str


@dataclass(frozen=True)
class ReleaseResult:
    release_id: str
    sku: str
    state: str
    image: Dict[str, Any]
    diagnostic: str


def publish_listing(request: ListingImageRequest, client: InfraiClient) -> ReleaseResult:
    """Upload, remove the background, then record a release decision."""
    try:
        image_id = client.upload(request.source_path)
        processed = client.background_remove(image_id)
    except InfraiError as exc:
        return ReleaseResult(request.release_id, request.sku, "rejected", {}, f"image service: {exc.code}")
    if not processed.get("url"):
        return ReleaseResult(request.release_id, request.sku, "rejected", processed, "image service returned no output URL")
    return ReleaseResult(request.release_id, request.sku, "released", processed, "background removed")
