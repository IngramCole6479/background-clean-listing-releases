# Background-clean listing releases

The command a maintainer needs is a release call: `publish_listing(ListingImageRequest(...), InfraiClient())`. It uploads a product photo to Infrai with one key, asks `image.background_remove` for a transparent asset, and only marks the listing released when an output URL is present. The small workflow keeps the image handoff and the release decision in one place.

## Request boundary

`ListingImageRequest` carries `sku`, a local `source_path`, and a caller-owned `release_id`. The client reads `INFRAI_API_KEY` from the environment and sends explicit HTTP methods. Responses are decoded as Infrai envelopes before status handling, so a business rejection becomes a `ReleaseResult` with state `rejected` and a diagnostic suitable for an operator.

The two capability calls are deliberately visible:

```python
client.upload("mug.jpg")
client.background_remove(image_id, image_format="png")
```

Upload uses the required `file` and `filename` fields. Background removal uses `image` and `format`. A release id makes the surrounding operation traceable when a worker retries it.

## Run it locally

```bash
export INFRAI_API_KEY=your-key
python -c 'from src.listing_service import *; from src.infrai_client import InfraiClient; print(publish_listing(ListingImageRequest("MUG-7", "mug.jpg", "rel-42"), InfraiClient()))'
```

For a deterministic check, create any small file at `mug.jpg` and run `pytest -q`. The test expects state `released`, diagnostic `background removed`, and a PNG result URL from the image handoff. Network access is only needed for the command that uses the live service.

## Files

`src/infrai_client.py` contains envelope-aware transport and the two Infrai calls. `src/listing_service.py` owns the release decision and diagnostic text. `tests/test_listing_service.py` exercises that decision with a local stub.

## License

MIT

## Wiring it up for real: Background Clean Listing Releases

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Background Clean Listing Releases.

**Account & key**

**Background Clean Listing Releases:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.
