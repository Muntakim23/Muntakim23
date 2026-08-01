import json
import requests
from bs4 import BeautifulSoup

USERNAME = "Muntakim23"

url = f"https://github.com/users/{USERNAME}/contributions"

response = requests.get(url)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

days = []

for rect in soup.select("rect[data-date]"):
    days.append({
        "date": rect["data-date"],
        "count": int(rect.get("data-count", 0)),
        "level": int(rect.get("data-level", 0))
    })

import os

os.makedirs("data", exist_ok=True)

with open("data/contributions.json", "w") as f:
    json.dump(days, f, indent=2)

print(f"Saved {len(days)} contribution days.")
