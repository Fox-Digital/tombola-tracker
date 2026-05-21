from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import re
from pathlib import Path

URL = "https://www.tombola.co.uk/bingo/games/bingo90"
OUTPUT = Path("tombola_players_online.csv")

def get_players_online():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            locale="en-GB",
            timezone_id="Europe/London",
            viewport={"width": 1366, "height": 900},
        )

        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)

        text = page.locator("body").inner_text()
        browser.close()

    match = re.search(r"Players online\s+([\d,]+)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"([\d,]+)\s+Players online", text, re.IGNORECASE)

    if not match:
        raise ValueError("Could not find players online number")

    return int(match.group(1).replace(",", ""))

players = get_players_online()
timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"

file_exists = OUTPUT.exists()

with OUTPUT.open("a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["timestamp_utc", "players_online"])
    writer.writerow([timestamp, players])

print(f"{timestamp}: {players} players online")
