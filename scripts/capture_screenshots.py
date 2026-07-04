"""Capture dashboard screenshots for portfolio README."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

TABS = [
    ("00-mission-control.png", "Mission Control"),
    ("09-interview-command-center.png", "Interview Command Center"),
    ("10-company-360.png", "Company 360"),
    ("11-people-map.png", "People Map"),
    ("12-role-deep-dive.png", "Role Deep Dive"),
    ("13-proof-assets.png", "Proof Assets"),
    ("01-overview-dashboard.png", "Overview"),
    ("02-company-ranking.png", "Company Ranking"),
    ("03-role-fit.png", "Role Fit"),
    ("04-sponsorship-signal.png", "Sponsorship Signal"),
    ("05-networking-map.png", "Networking Map"),
    ("06-interview-prep.png", "Interview Prep"),
    ("07-recommendations.png", "Recommendations"),
    ("08-export-sql-demo.png", "Export"),
]


async def main() -> int:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright not installed")
        return 1

    url = "http://localhost:8501"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)

        for filename, tab_name in TABS:
            tab = page.get_by_role("tab", name=tab_name)
            await tab.click()
            await page.wait_for_timeout(1500)
            path = SCREENSHOTS / filename
            await page.screenshot(path=str(path), full_page=True)
            print(f"Captured {path.name}")

        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
