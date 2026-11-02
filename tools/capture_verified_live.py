"""Capture genuine YouCam UI results after a real API scan, never sample results.

This script requires a running Serein backend on localhost with a valid YouCam
API key configured on the server and a photograph that you are authorized to use.
No API key is read or transferred by the screenshot tool.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from datetime import datetime, timezone

BASE = "http://127.0.0.1:8011"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "LIVE_YOUCAM_SCREENSHOTS"


def check_server():
    try:
        with urlopen(BASE + "/api/config", timeout=6) as response:
            config = json.load(response)
    except (URLError, OSError, ValueError) as exc:
        raise RuntimeError("Serein isn't running on port 8011. Run START_WINDOWS.bat first.") from exc
    if config.get("mode") != "live":
        raise RuntimeError("A YouCam key has NOT been loaded. Use CONNECT_YOUCAM_WINDOWS.bat and restart START_WINDOWS.bat; this program will NOT create fake API results.")


def click_nav(page, route):
    page.locator(f'.nav-item[data-route="{route}"]').first.click()
    page.wait_for_timeout(700)


def capture(page, filename):
    page.screenshot(path=str(OUTPUT / filename), animations="disabled", full_page=False)
    print("  Captured:", filename)


def main():
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: capture_verified_live.py YOUR_PHOTO.jpg")
    image = Path(sys.argv[1].strip('"')).expanduser()
    if not image.exists() or not image.is_file():
        raise RuntimeError(f"Photo not found: {image}")
    if image.suffix.lower() not in ('.jpg','.jpeg','.png'):
        raise RuntimeError('Use a JPG or PNG photo.')
    if image.stat().st_size > 9*1024*1024:
        raise RuntimeError('Photo larger than 9MB. Resize it first.')
    check_server()
    print("\nThis will upload the selected photo to Perfect Corp's YouCam API for skin analysis.")
    print("The screenshots may contain information about your cosmetic appearance.")
    answer = input("Do you consent to upload this photo for that purpose? Type YES: ").strip()
    if answer != 'YES':
        raise RuntimeError('Consent not given. The photo has NOT been uploaded.')

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError as exc:
        raise RuntimeError('Install Playwright: python -m pip install playwright') from exc

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=False)
        except Exception:
            try:
                browser = playwright.chromium.launch(headless=False)
            except Exception as exc:
                raise RuntimeError('Could not start a browser. Install Chrome or run: python -m playwright install chromium') from exc
        context = browser.new_context(viewport={"width": 1500, "height": 1000}, device_scale_factor=1)
        page = context.new_page()
        page.set_default_timeout(14000)
        try:
            page.goto(BASE, wait_until="domcontentloaded")
            page.wait_for_function("document.querySelector('#connectionBadge')?.textContent.includes('API key loaded')", timeout=15000)
            click_nav(page, 'scan')
            page.locator('#photoInput').set_input_files(str(image))
            page.wait_for_timeout(900)
            page.locator('#consent').check()
            page.locator('[data-action="runScan"]').click()
            print('Processing the photo through the actual YouCam endpoint. No sample results will be used.')
            try:
                page.wait_for_function("""() => {
                    let entries = JSON.parse(localStorage.getItem('serein.skin.journal.v1') || '[]');
                    let verified = Array.isArray(entries) && entries[0]?.source === 'youcam-live'
                        && document.querySelector('#connectionBadge')?.textContent.includes('YouCam scan verified');
                    let error = document.querySelector('#toast.error.show');
                    return verified || Boolean(error);
                }""", timeout=290000, polling=650)
            except PWTimeout as exc:
                raise RuntimeError('The real YouCam scan timed out. No screenshots were saved.') from exc
            if page.locator('#toast.error.show').count():
                raise RuntimeError('YouCam API request failed: ' + page.locator('#toast').inner_text() + '. No screenshots were saved.')
            entry = page.evaluate("JSON.parse(localStorage.getItem('serein.skin.journal.v1'))[0]")
            if entry.get('source') != 'youcam-live' or not entry.get('metrics'):
                raise RuntimeError('Provider result was not verified. No screenshots were saved.')
            OUTPUT.mkdir(exist_ok=True)
            page.wait_for_timeout(700)
            capture(page,'01-Insights-VERIFIED-YOUCAM.png')
            click_nav(page,'ritual');capture(page,'02-Routine-VERIFIED-YOUCAM.png')
            click_nav(page,'journal');capture(page,'03-Journal-VERIFIED-YOUCAM.png')
            click_nav(page,'home');capture(page,'04-Overview-VERIFIED-YOUCAM.png')
            click_nav(page,'scan');capture(page,'05-Scan-VERIFIED-YOUCAM.png')
            report={
              "verified_source": "youcam-live",
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "metrics_returned": len(entry['metrics']),
              "screenshots": [p.name for p in sorted(OUTPUT.glob('*.png'))],
              "notes": "Captured by Playwright after Serein's live backend flow returned real metrics; no sample results were loaded."
            }
            (OUTPUT/'VERIFICATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            print('\nSUCCESS: Screenshots were taken only after a real YouCam scan.\nSaved in:',OUTPUT)
        finally:
            context.close();browser.close()

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print('\nERROR:',exc)
        sys.exit(1)
