#!/usr/bin/env python3
"""Pull posts and reels from an Instagram Business/Creator account via the official Graph API.

Requires an Instagram Business or Creator account linked to a Facebook Page,
and a Meta access token with instagram_basic + pages_read_engagement scopes.
See README.md for setup steps.
"""
import argparse
import json
import os
import sys

import requests

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

MEDIA_FIELDS = (
    "id,caption,media_type,media_product_type,media_url,permalink,"
    "thumbnail_url,timestamp,like_count,comments_count,"
    "children{media_url,media_type}"
)


def fetch_all_media(ig_user_id: str, access_token: str) -> list[dict]:
    media = []
    url = f"{GRAPH_API_BASE}/{ig_user_id}/media"
    params = {"fields": MEDIA_FIELDS, "access_token": access_token, "limit": 50}

    while url:
        response = requests.get(url, params=params, timeout=30)
        payload = response.json()

        if response.status_code != 200:
            error = payload.get("error", {})
            raise RuntimeError(
                f"Graph API error {error.get('code')}: {error.get('message')} "
                f"(check that the token hasn't expired and the account is Business/Creator)"
            )

        media.extend(payload.get("data", []))
        url = payload.get("paging", {}).get("next")
        params = None  # 'next' URL already includes all query params

    return media


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--media-type",
        choices=["ALL", "REELS", "IMAGE", "VIDEO", "CAROUSEL_ALBUM"],
        default="ALL",
        help="Filter by media_product_type/media_type (default: ALL)",
    )
    parser.add_argument(
        "--output",
        default="instagram_content.json",
        help="Output JSON file path (default: instagram_content.json)",
    )
    args = parser.parse_args()

    access_token = os.environ.get("IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID")

    if not access_token or not ig_user_id:
        sys.exit(
            "Missing IG_ACCESS_TOKEN and/or IG_BUSINESS_ACCOUNT_ID environment variables.\n"
            "See README.md for how to get these from Meta for Developers."
        )

    media = fetch_all_media(ig_user_id, access_token)

    if args.media_type == "REELS":
        media = [m for m in media if m.get("media_product_type") == "REELS"]
    elif args.media_type != "ALL":
        media = [m for m in media if m.get("media_type") == args.media_type]

    with open(args.output, "w") as f:
        json.dump(media, f, indent=2)

    print(f"Fetched {len(media)} items -> {args.output}")


if __name__ == "__main__":
    main()
