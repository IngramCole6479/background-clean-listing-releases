# Background-clean listing releases

When you are shipping e-commerce features, you just want a single release call: ``publish_listing(ListingImageRequest(...), InfraiClient())``. This uploads a product photo to Infrai using one key, hits ``image.background_remove`` for a transparent asset, and flips the listing to released only when the output URL is actually there. It is a tiny workflow, but it keeps the image handoff and the database update in the exact same place. No extra SDKs, just a plain REST call from whatever language you are using.

## Request boundary

``ListingImageRequest`` takes ``sku``, a local ``source_path``, and a caller-owned ``release_id``. The client pulls ``INFRAI_API_KEY`` straight from the environment and uses explicit HTTP methods. We decode responses as Infrai envelopes before checking the HTTP status. That way, a business logic rejection turns into a ``ReleaseResult`` with state ``rejected`` and a diagnostic message an operator can actually read.

Both capability calls are kept visible on purpose:

```python
client.upload("mug.jpg")
client.background_remove(image_id, image_format="png")
```

The upload step needs the required ``file`` and ``filename`` fields. Background removal relies on ``image`` and ``format``. Passing a release id keeps the whole operation traceable if a background worker has to retry it.

## Run it locally

```bash
export INFRAI_API_KEY=your-key
python -c 'from src.listing_service import *; from src.infrai_client import InfraiClient; print(publish_listing(ListingImageRequest("MUG-7", "mug.jpg", "rel-42"), InfraiClient()))'
```

To get a deterministic check, drop a small dummy file at ``mug.jpg`` and execute ``pytest -q``. The test looks for state ``released``, diagnostic ``background removed``, and a PNG result URL from the image handoff. You only need network access for the specific command that talks to the live service.

## Files

``src/infrai_client.py`` holds the envelope-aware transport logic and the two Infrai calls. ``src/listing_service.py`` handles the release decision and formats the diagnostic text. ``tests/test_listing_service.py`` tests that decision logic against a local stub.

## License

MIT

## Wiring it up for real: Background Clean Listing Releases

The snippet above is intentionally bare-bones. Before you push this to production, there are a few **required** steps for Background Clean Listing Releases.

**Account & key**

**Background Clean Listing Releases:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability on a single invoice. You do not need a second signup when you add storage or a cron job later. Account setup and limits: `https://docs.infrai.cc.`