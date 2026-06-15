"""
Nursing Govt Exam & Job Tracker - Scraper
Checks job portal listing pages for nursing-related notifications,
keeps a running data store (data/notices.json), and flags new items.

Designed to run unattended on a schedule (GitHub Actions).
No API keys required.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "notices.json")

# Keywords that indicate a nursing-related govt exam/job notice.
NURSING_KEYWORDS = [
    "nurse", "nursing", "norcet", "anm", "gnm", "staff nurse",
    "nursing officer", "nursing superintendent", "nursing tutor",
    "sister tutor", "midwifery", "paramedical nursing",
]

# Source pages to scan. Each entry: name, url, org tag (for filtering on dashboard),
# and a CSS-ish hint for where the listing links live (handled generically below).
SOURCES = [
    {
        "name": "Sarkari Result - Latest Jobs",
        "url": "https://www.sarkariresult.com/latestjob/",
        "org": "aggregator",
    },
    {
        "name": "FreeJobAlert - Nursing Jobs",
        "url": "https://www.freejobalert.com/nursing-jobs/",
        "org": "aggregator",
    },
    {
        "name": "NursingJobAlert - Nursing Officer Vacancy",
        "url": "https://nursingjobalert.com/nursing-officer-vacancy/",
        "org": "aggregator",
    },
    {
        "name": "AIIMS Exams (NORCET) - Official",
        "url": "https://www.aiimsexams.ac.in/",
        "org": "aiims",
    },
    {
        "name": "ESIC - Official Recruitment",
        "url": "https://www.esic.gov.in/recruitments",
        "org": "esic",
    },
]


def load_existing():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_run": None, "notices": []}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_nursing_related(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in NURSING_KEYWORDS)


def fetch_source(source):
    """Fetch a source page and extract candidate (title, link) pairs."""
    items = []
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=25)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARN] Failed to fetch {source['name']}: {e}", file=sys.stderr)
        return items

    soup = BeautifulSoup(resp.text, "lxml")

    # Generic approach: every <a> tag with non-trivial text is a candidate.
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]

        if not title or len(title) < 8:
            continue
        if not is_nursing_related(title):
            continue

        # Resolve relative URLs
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(source["url"], href)
        elif not href.startswith("http"):
            from urllib.parse import urljoin
            href = urljoin(source["url"], href)

        items.append({
            "title": title,
            "link": href,
            "source": source["name"],
            "org": source["org"],
        })

    return items


def classify_status(title):
    """Best-effort status tag based on title text."""
    t = title.lower()
    if "result" in t or "merit" in t or "cut off" in t or "cutoff" in t:
        return "result"
    if "admit card" in t:
        return "admit-card"
    if "extend" in t or "last date" in t or "closing" in t:
        return "open"
    if "notification" in t and ("out" in t or "released" in t):
        return "open"
    return "open"


def main():
    data = load_existing()
    existing_links = {n["link"] for n in data["notices"]}

    new_items = []
    all_seen = []

    for source in SOURCES:
        print(f"Checking: {source['name']} ...")
        found = fetch_source(source)
        all_seen.extend(found)

    # Dedupe by link
    seen_links = set()
    deduped = []
    for item in all_seen:
        if item["link"] in seen_links:
            continue
        seen_links.add(item["link"])
        deduped.append(item)

    for item in deduped:
        if item["link"] not in existing_links:
            item["status"] = classify_status(item["title"])
            item["first_seen"] = datetime.now(timezone.utc).isoformat()
            new_items.append(item)

    if new_items:
        data["notices"] = new_items + data["notices"]
        # Keep the list to a reasonable size
        data["notices"] = data["notices"][:150]
        print(f"Found {len(new_items)} new nursing-related notice(s).")
    else:
        print("No new nursing-related notices found this run.")

    data["last_run"] = datetime.now(timezone.utc).isoformat()
    save_data(data)


if __name__ == "__main__":
    main()
