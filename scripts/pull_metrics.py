#!/usr/bin/env python3
"""Pull GSC + PSI metrics into METRICS/ as dated JSON. Fails loudly (exit 1)
so the loop can hard-stop on empty ingestion.

Required env: GSC_SA_KEY (service-account JSON), GSC_SITE
(e.g. sc-domain:charterflightnetwork.com), PSI_API_KEY.
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

from google.oauth2 import service_account
from googleapiclient.discovery import build

OUT = "METRICS"
os.makedirs(OUT, exist_ok=True)
today = datetime.date.today().isoformat()
# GSC data lags 2-3 days behind
target = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()

# ---- Google Search Console ----
key = json.loads(os.environ["GSC_SA_KEY"])
site = os.environ["GSC_SITE"]
creds = service_account.Credentials.from_service_account_info(
    key, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
)
svc = build("searchconsole", "v1", credentials=creds)
gsc = {}
try:
    for dims in (["query"], ["page"]):
        body = {
            "startDate": (datetime.date.today() - datetime.timedelta(days=31)).isoformat(),
            "endDate": target,
            "dimensions": dims,
            "rowLimit": 25000,
            "dataState": "final",
        }
        gsc["_".join(dims)] = (
            svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])
        )
except Exception as e:
    print(f"FAIL GSC: {e}", file=sys.stderr)
    sys.exit(1)
if not gsc.get("query") and not gsc.get("page"):
    print("FAIL GSC: empty result", file=sys.stderr)
    sys.exit(1)
json.dump(gsc, open(f"{OUT}/gsc_{today}.json", "w"), indent=2)

# ---- PageSpeed Insights ----
psi_key = os.environ["PSI_API_KEY"]
pages = [
    "https://charterflightnetwork.com/",
    "https://charterflightnetwork.com/canada/northern-ontario/thunder-bay",
    "https://charterflightnetwork.com/quote",
]
psi = {}
for url in pages:
    api = (
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={urllib.parse.quote(url)}&strategy=mobile&category=performance"
        f"&category=seo&key={psi_key}"
    )
    try:
        data = json.load(urllib.request.urlopen(api, timeout=90))
        psi[url] = {
            c: data["lighthouseResult"]["categories"][c]["score"]
            for c in data["lighthouseResult"]["categories"]
        }
    except Exception as e:
        print(f"WARN PSI {url}: {e}", file=sys.stderr)
json.dump(psi, open(f"{OUT}/psi_{today}.json", "w"), indent=2)
print(f"OK metrics written for {today}")
