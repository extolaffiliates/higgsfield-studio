# Instagram Content Fetcher

Pulls posts and reels from an Instagram **Business or Creator** account using
Meta's official Graph API. Only works for accounts you administer — this is
not a scraper and cannot read accounts you don't manage.

## Requirements

- The Instagram account must be a **Business or Creator account** (not
  Personal), linked to a **Facebook Page** you administer. Both are required
  by Meta's API, no exceptions.

## Setup

1. Create an app at [developers.facebook.com](https://developers.facebook.com/apps).
2. Add the **Instagram Graph API** and **Facebook Login** products to the app.
3. In [Graph API Explorer](https://developers.facebook.com/tools/explorer/),
   select your app, generate a User Access Token with these permissions:
   `instagram_basic`, `pages_show_list`, `pages_read_engagement`.
4. Exchange it for a **long-lived token** (60-day expiry) — the Explorer's
   "Access Token Debugger" has a one-click extend option. Note the expiry
   date; the token needs re-generating before then unless you set up a
   Business Manager System User token (no expiry, more setup).
5. Find your Instagram Business Account ID: `GET /{page-id}?fields=instagram_business_account`
   in Graph API Explorer, using the Facebook Page linked to your IG account.
6. Copy `.env.example` to `.env` and fill in `IG_ACCESS_TOKEN` and
   `IG_BUSINESS_ACCOUNT_ID`.

## Usage

### Locally

```bash
pip install -r requirements.txt
export $(cat .env | xargs)  # or use python-dotenv / your own env loading

python fetch_instagram_content.py --media-type ALL --output instagram_content.json
python fetch_instagram_content.py --media-type REELS --output reels_only.json
```

### Via GitHub Actions (recommended if tokens live in repo secrets)

The workflow at `.github/workflows/instagram-fetch.yml` runs this script in
CI, reading the token from GitHub Actions secrets — the token is never
exposed in logs or committed anywhere.

1. In the repo: **Settings → Secrets and variables → Actions**, add:
   - `IG_ACCESS_TOKEN`
   - `IG_BUSINESS_ACCOUNT_ID`
2. Go to the **Actions** tab → "Fetch Instagram Content" → **Run workflow**,
   pick a media type filter, run it.
3. Download the `instagram-content` artifact from the completed run for the
   resulting JSON.

Output is a JSON array of media objects: caption, media type, media URL,
permalink, timestamp, like/comment counts, and thumbnail for video/reels.

## Known limitation

Long-lived tokens expire after 60 days. If the script starts failing with an
auth error after it previously worked, regenerate the token — this is the
most common failure mode, not a bug.
