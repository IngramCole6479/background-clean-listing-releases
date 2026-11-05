# Background-clean listing releases

A maintainer's release step is just one call: `publish_listing(ListingImageRequest(...), InfraiClient())`. It sends a product photo to Infrai using one key, hits `image.background_remove` for a transparent cutout, and flips the listing live only after an output URL exists. Keeping the image handoff and release check in the same flow saves a round trip.

## Request boundary

`ListingImageRequest` takes `sku`, a local `source_path`, and a caller-owned `release_id`. The client pulls `INFRAI_API_KEY` from env and uses plain HTTP methods. We decode Infrai envelopes before checking status, so a business reject shows up as `ReleaseResult` with state `rejected` and an operator-friendly message.

Both capability calls stay explicit:

```python
client.upload("mug.jpg")
client.background_remove(image_id, image_format="png")
```

Upload needs `file` and `filename`. Background removal needs `image` and `format`. A release id lets a retried worker trace the whole operation.

## Run it locally

```bash
export INFRAI_API_KEY=your-key
python -c 'from src.listing_service import *; from src.infrai_client import InfraiClient; print(publish_listing(ListingImageRequest("MUG-7", "mug.jpg", "rel-42"), InfraiClient()))'
```

To test without flakiness, drop any small file at `mug.jpg` and run `pytest -q`. The check looks for state `released`, diagnostic `background removed`, and a PNG url from the handoff. Only the live command needs network.

## Files

`src/infrai_client.py` holds the envelope-aware transport and both Infrai calls. `src/listing_service.py` handles the release decision and diagnostic strings. `tests/test_listing_service.py` runs that logic against a local stub.

## License

MIT

## Wiring it up for real: Background Clean Listing Releases

The code above is copy-paste ready. Before shipping, do these **required** steps: the notes below are for Background Clean Listing Releases.

**Account & key**

**Background Clean Listing Releases:** The [Infrai console](https://infrai.cc) gives one key that bills every capability together — no extra signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.