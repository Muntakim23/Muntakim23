#!/usr/bin/env python3

import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "Muntakim23")

URL = f"https://github.com/users/{USERNAME}/contributions"

BASE = os.path.dirname(__file__)
OUT_PATH = os.path.join(BASE, "..", "data", "contributions.json")


def fetch_days():
    r = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")

    if not cells:
        print("GitHub contribution calendar not found.")
        sys.exit(1)

    days = []

    for td in cells:
        date = td.get("data-date")
        if not date:
            continue

        td_id = td.get("id")

        tooltip = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None

        text = tooltip.get_text(strip=True) if tooltip else ""

        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0

        days.append(
            {
                "date": date,
                "count": count,
            }
        )

    days.sort(key=lambda x: x["date"])

    return days


def current_streak(days):
    idx = len(days) - 1

    if idx >= 0 and days[idx]["count"] == 0:
        idx -= 1

    streak = 0

    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1

    return streak


def longest_streak(days):
    longest = 0
    run = 0

    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    return longest


def build(days):
    total = sum(d["count"] for d in days)

    best = max(days, key=lambda x: x["count"])

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "range": {
            "start": days[0]["date"],
            "end": days[-1]["date"],
        },
        "total_contributions": total,
        "current_streak": {
            "length": current_streak(days)
        },
        "longest_streak": {
            "length": longest_streak(days)
        },
        "best_day": best,
        "days": days,
    }


if __name__ == "__main__":

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    days = fetch_days()

    data = build(days)

    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("Saved:", OUT_PATH)
