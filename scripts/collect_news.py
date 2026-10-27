#!/usr/bin/env python3
"""Collect attributed public article links, never treating reporting as verified case records."""
import datetime as dt
import json
import pathlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import email.utils
import html

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "daily-news.json"
QUERIES = [
    '"child sexual abuse" lawsuit',
    '"sexual abuse" school lawsuit',
    '"sexual abuse" church settlement',
    '"child sexual abuse" criminal court',
    '"sexual abuse" youth organization lawsuit',
    '"sexual abuse" university lawsuit',
    '"child sexual abuse" trial sentencing',
]
HEADERS = {"User-Agent": "SurvivorJusticeNews/1.0 (public news headlines; contact through repository)"}
def iso(text):
    try:
        return email.utils.parsedate_to_datetime(text).astimezone(dt.timezone.utc).isoformat()
    except Exception:
        return ""
def collect():
    items = {}
    if OUT.exists():
        try:
            for item in json.loads(OUT.read_text()).get("items", []):
                if isinstance(item, dict) and item.get("url"):
                    items[item["url"]] = item
        except (ValueError, OSError, AttributeError):
            pass
    for query in QUERIES:
        qs = urllib.parse.urlencode({"q":query,"hl":"en-US","gl":"US","ceid":"US:en"})
        url = "https://news.google.com/rss/search?" + qs
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as response:
                root = ET.fromstring(response.read(2_000_000))
        except Exception as exc:
            print("Feed unavailable:", query, str(exc)[:120])
            continue
        for entry in root.findall("./channel/item"):
            title = html.unescape((entry.findtext("title") or "").strip())[:240]
            link = (entry.findtext("link") or "").strip()
            source = (entry.findtext("source") or "News publisher").strip()[:110]
            published = iso(entry.findtext("pubDate") or "")
            if not title or not link.startswith("https://"):
                continue
            if link not in items:
                items[link] = {"title":title,"url":link,"source":source,
                               "published":published,"status":"Unreviewed news lead"}
    values = sorted(items.values(), key=lambda x:x.get("published",""),reverse=True)[:500]
    OUT.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).isoformat(),
                               "items": values},ensure_ascii=False,indent=2)+"\n")
    print("Collected",len(values),"headlines")
if __name__ == "__main__":
    collect()
