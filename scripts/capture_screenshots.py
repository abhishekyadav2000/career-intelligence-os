"""Capture dashboard screenshots for portfolio README."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

# (filename, tab display name, nav group from dashboard/navigation.py)
TABS = [
    ("00-mission-control.png", "Mission Control", "Execute"),
    ("09-interview-command-center.png", "Command Center", "Tools"),
    ("10-company-360.png", "Company 360", "Intelligence"),
    ("11-people-map.png", "People Map", "Intelligence"),
    ("12-role-deep-dive.png", "Role Deep Dive", "Intelligence"),
    ("13-proof-assets.png", "Proof Assets", "Intelligence"),
    ("01-overview-dashboard.png", "Overview", "Analytics"),
    ("02-company-ranking.png", "Company Ranking", "Analytics"),
    ("03-role-fit.png", "Role Fit", "Analytics"),
    ("04-sponsorship-signal.png", "Sponsorship Signal", "Analytics"),
    ("05-networking-map.png", "Networking Map", "Tools"),
    ("06-interview-prep.png", "Interview Prep", "Tools"),
    ("07-recommendations.png", "Recommendations", "Analytics"),
    ("08-export-sql-demo.png", "Export", "Tools"),
]


async def select_view(page, tab_name: str, nav_group: str) -> None:
    group_label = page.locator('label[data-baseweb="radio"]').filter(
        has=page.get_by_text(nav_group, exact=True)
    )
    await group_label.first.click()
    await page.wait_for_timeout(1200)
    tab = page.get_by_role("tab", name=tab_name, exact=True)
    if await tab.count():
        await tab.first.click()
        await page.wait_for_timeout(1500)


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

        for filename, tab_name, nav_group in TABS:
            await select_view(page, tab_name, nav_group)
            path = SCREENSHOTS / filename
            await page.screenshot(path=str(path), full_page=True)
            print(f"Captured {path.name}")

        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
