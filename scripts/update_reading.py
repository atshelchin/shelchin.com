#!/usr/bin/env python3
"""抓取 data/feeds.toml 里的订阅源，生成 data/reading.json，供 /reading 页面使用。

只用 Python 标准库（需要 3.11+），本地和 GitHub Actions 里都能直接运行：

    python3 scripts/update_reading.py

只保存标题、链接、作者和日期，不保存正文。某个订阅源抓取失败时，沿用上一次的结果，
不会把它的文章清空。内容没有变化时不改写文件，避免产生无意义的提交。
"""

import html
import json
import re
import sys
import tomllib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "data" / "feeds.toml"
OUTPUT_PATH = ROOT / "data" / "reading.json"

ATOM = "{http://www.w3.org/2005/Atom}"
RSS1 = "{http://purl.org/rss/1.0/}"
DC = "{http://purl.org/dc/elements/1.1/}"

USER_AGENT = "Mozilla/5.0 (compatible; shelchin.com reading list; +https://shelchin.com/reading/)"
TIMEOUT_SECONDS = 20
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def text_of(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def clean(value):
    """去掉标题里的 HTML 标签和实体，合并空白。"""
    value = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)  # RSS: RFC 822
    except (TypeError, ValueError, IndexError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))  # Atom: ISO 8601
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def rss_author(value):
    """RSS 的 <author> 常写成 "email (Name)"，只取名字；纯邮箱不要。"""
    value = clean(value)
    match = re.search(r"\(([^)]+)\)", value)
    if match:
        return match.group(1).strip()
    return "" if "@" in value else value


def atom_link(entry):
    links = entry.findall(f"{ATOM}link")
    for link in links:
        if link.get("rel", "alternate") == "alternate" and link.get("href"):
            return link.get("href")
    for link in links:
        if link.get("href"):
            return link.get("href")
    entry_id = text_of(entry.find(f"{ATOM}id"))
    return entry_id if entry_id.startswith("http") else ""


def parse_feed(data):
    """返回 [(title, link, author, datetime | None)]，兼容 Atom、RSS 2.0 和 RSS 1.0。"""
    root = ET.fromstring(data.lstrip())
    entries = []

    if root.tag == f"{ATOM}feed":
        feed_author = text_of(root.find(f"{ATOM}author/{ATOM}name"))
        for entry in root.findall(f"{ATOM}entry"):
            published = entry.find(f"{ATOM}published")
            if published is None:
                published = entry.find(f"{ATOM}updated")
            entries.append((
                clean(text_of(entry.find(f"{ATOM}title"))),
                atom_link(entry),
                clean(text_of(entry.find(f"{ATOM}author/{ATOM}name"))) or clean(feed_author),
                parse_date(text_of(published)),
            ))
    elif root.tag == "rss":
        for item in root.findall("channel/item"):
            date = text_of(item.find("pubDate")) or text_of(item.find(f"{DC}date"))
            entries.append((
                clean(text_of(item.find("title"))),
                text_of(item.find("link")),
                clean(text_of(item.find(f"{DC}creator"))) or rss_author(text_of(item.find("author"))),
                parse_date(date),
            ))
    elif root.tag.endswith("RDF"):
        for item in root.findall(f"{RSS1}item"):
            entries.append((
                clean(text_of(item.find(f"{RSS1}title"))),
                text_of(item.find(f"{RSS1}link")),
                clean(text_of(item.find(f"{DC}creator"))),
                parse_date(text_of(item.find(f"{DC}date"))),
            ))
    else:
        raise ValueError(f"unrecognized feed format: {root.tag}")

    return entries


def fetch(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/atom+xml, application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    })
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def feed_id(feed):
    if feed.get("id"):
        return feed["id"]
    parsed = urlparse(feed["url"])
    return re.sub(r"[^a-z0-9]+", "-", (parsed.netloc + parsed.path).lower()).strip("-")


def build_item(title, link, author, dt, feed, fid, tz):
    # 配置里写了 author 就用配置的（保证页面上是英文），没写才用订阅源自带的
    author = feed.get("author") or author
    name = feed["name"]
    # 作者名已经出现在订阅源名字里时不重复显示
    source = name if not author or author.lower() in name.lower() else f"{author} · {name}"
    item = {
        "title": title or "(Untitled)",
        "link": urljoin(feed.get("site") or feed["url"], link) if link else feed.get("site", ""),
        "author": author,
        "source": source,
        "feed": fid,
        "lang": feed["lang"],
    }
    if dt is None:
        return {**item, "date": "", "day": "", "ym": "unknown", "ym_label": "Undated", "ts": 0}
    local = dt.astimezone(tz)
    return {
        **item,
        "date": local.strftime("%Y-%m-%d"),
        "day": f"{MONTHS[local.month - 1][:3]} {local.day}",
        "ym": local.strftime("%Y-%m"),
        "ym_label": f"{MONTHS[local.month - 1]} {local.year}",
        "ts": int(dt.timestamp()),
    }


def main():
    config = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    settings = config.get("settings", {})
    tz = ZoneInfo(settings.get("timezone", "Asia/Shanghai"))
    max_per_feed = int(settings.get("max_per_feed", 30))
    max_items = int(settings.get("max_items", 500))
    languages = config.get("languages", {})
    feeds = config.get("feeds", [])

    previous = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")) if OUTPUT_PATH.exists() else {}
    previous_items = {}
    for item in previous.get("items", []):
        previous_items.setdefault(item["feed"], []).append(item)

    items, feed_rows, failures = [], [], 0
    for feed in feeds:
        missing = [key for key in ("name", "url", "lang") if not feed.get(key)]
        if missing:
            sys.exit(f"Feed {feed} is missing: {', '.join(missing)}")
        # 不收 Shorts：YouTube 只能订只含长视频的 UULF 播放列表，频道订阅源会混进 Shorts
        if "youtube.com/feeds/" in feed["url"] and "playlist_id=UULF" not in feed["url"]:
            sys.exit(f"{feed['name']}: YouTube feeds must use playlist_id=UULF<channel id without UC> "
                     "(long videos only, no Shorts)")
        if feed["lang"] not in languages:
            print(f"! {feed['name']}: lang = {feed['lang']!r} is not listed in [languages]; showing it as is")

        fid = feed_id(feed)
        try:
            entries = parse_feed(fetch(feed["url"]))
            feed_items = [build_item(*entry, feed, fid, tz) for entry in entries]
            feed_items.sort(key=lambda item: item["ts"], reverse=True)
            feed_items = feed_items[:max_per_feed]
            ok = True
            print(f"✓ {feed['name']}: {len(feed_items)} posts")
        except Exception as error:  # noqa: BLE001 —— 单个订阅源出错不影响其他订阅源
            feed_items = previous_items.get(fid, [])
            ok = False
            failures += 1
            print(f"✗ {feed['name']}: {error} (keeping {len(feed_items)} posts from the last run)")

        items.extend(feed_items)
        feed_rows.append({
            "id": fid,
            "name": feed["name"],
            "author": feed.get("author", ""),
            "site": feed.get("site") or feed["url"],
            "url": feed["url"],
            "lang": feed["lang"],
            "lang_name": languages.get(feed["lang"], feed["lang"]),
            "count": len(feed_items),
            "ok": ok,
        })

    items.sort(key=lambda item: item["ts"], reverse=True)
    items = items[:max_items]

    used = {row["lang"] for row in feed_rows}
    ordered = [k for k in languages if k in used] + sorted(used - languages.keys())
    content = {
        "languages": [
            {"key": k, "name": languages.get(k, k), "count": sum(1 for i in items if i["lang"] == k)}
            for k in ordered
        ],
        "feeds": feed_rows,
        "items": items,
    }
    unchanged = {key: previous.get(key) for key in content} == content
    if unchanged:
        print("No changes; data/reading.json left as is")
    else:
        updated = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
        OUTPUT_PATH.write_text(
            json.dumps({"updated": updated, **content}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote data/reading.json: {len(items)} posts from {len(feed_rows)} feeds")

    if feeds and failures == len(feeds):
        sys.exit("All feeds failed")


if __name__ == "__main__":
    main()
