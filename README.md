# IMPORTANT: Live API Screenshot Capture

To capture real YouCam results, see [README-LIVE-RESULTS.md](README-LIVE-RESULTS.md). Screenshots are **not generated unless an authenticated API scan succeeds**. No key is shipped with the project.

# Serein — the skin-to-shelf studio

**Designed and developed by Abu Hurrairah · 2026**

An editorial, mobile-responsive, privacy-aware hackathon prototype that translates **real YouCam Skin Analysis v2.1** appearance metrics into explainable cosmetic routines, category-level shopping decisions, and browser-local journaling.

> **Honest demo policy:** The app ships with a labelled *sample experience* so the complete UI is testable without API credentials. This is illustrative and **not a YouCam analysis**. A real YouCam API key is required to process an actual selfie. We have not independently validated the live provider calls without such credentials.

## Start (Windows PowerShell — Python 3.12)

```powershell
cd "C:\path\to\Serein-Skin-Studio"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011 --reload
```

Open **http://127.0.0.1:8011**. Select **Explore sample results** on the Skin Scan page to try the complete flow without a key.

### Using your existing global Python (no virtual environment)

```powershell
$PY = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
& $PY -m pip install -r requirements.txt
Copy-Item .env.example .env
& $PY -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

For macOS/Linux: `python3 -m pip install -r requirements.txt && cp .env.example .env && python3 -m uvicorn app.main:app --port 8011`.

## Enable the actual YouCam API

1. Register at https://yce.perfectcorp.com/ai-api . Claim your hackathon units and create your API key in Account > API Key.
2. Open `.env` and set `YOUCAM_API_KEY=YOUR_REAL_KEY` (**never commit this file**).
3. Restart the server. The top badge changes from "Sample mode" to "YouCam API connected".
4. Take or upload a well-lit selfie (JPG/PNG; min short side 480px; <=9MB), tick consent, and click **Analyse my skin**. A real API call may consume units.
5. The backend uploads the re-encoded JPEG via `POST /s2s/v2.0/file` followed by signed `PUT`, creates a task via `POST /s2s/v2.1/task/skin-analysis`, and the frontend polls `GET /s2s/v2.1/task/skin-analysis/{task_id}` until success/error.
6. Inspect the live returned cosmetic appearance scores on My insights. If a metric was not returned, we don't invent it.

Official docs: https://docs.perfectcorp.com/reference/ai_skin_analysis/v2.1 and https://docs.perfectcorp.com/reference/file

## Professional edition v1.2: why you may see an old footer

This release uses **http://127.0.0.1:8011** instead of port 8000. If an older edition is still running on 8000, that old page will continue to show the old footer. Double-click `START_WINDOWS.bat` **from this v1.2 folder** and use the 8011 URL. A visible `SEREIN 1.2` label and **Designed & Developed by Abu Hurrairah** appear in the footer on every page. If needed, use Ctrl+Shift+R to refresh. Your YouCam key stays in `.env`; copy it from the previous folder into this one yourself.

The included **`DEVPOST_THUMBNAIL.png`** is a 3:2 JPG/PNG-compliant thumbnail created from a genuine capture of the prototype UI, rather than a fabricated screenshot. It does not imply that a live API analysis was successfully performed.

## The 2026 editorial refresh

- Distinctive visual identity with warm mineral colours, restrained serif typography, and original illustrated study art.
- A clearer onboarding experience, prominent demo pathway, simplified navigation, responsive mobile menu, and improved keyboard focus styles.
- **Abu Hurrairah** credited prominently in the sidebar, About dialog, page metadata, and footer on every screen.
- Accessible reduced-motion support, labelled navigation, working mobile overlay, and clearer key-status text ("API key configured" does **not** assert provider availability).
- Browser-rendered demo UI reference screenshots are provided in `screenshots/` for review. **They demonstrate the sample interface, not a successful live YouCam API response.** For judging, take your own running-app captures using the screenshot tool or browser after your backend is running.

## Pages
- **Overview:** the mission, product narrative, and interactive navigation.
- **Skin Scan:** photo upload or camera capture, quality tips, consent, real task execution or labelled sample journey.
- **My Insights:** actual returned appearance metrics, transparent priority ranking, and clear score interpretation.
- **My Ritual:** morning/evening routines, 3 essentials + up to 2 optional categories, explainable 'why', editable basket, illustrative three-tier price budgeting.
- **Skin Journal:** chronological check-ins, reflections, localStorage persistence, CSV download and delete.

## Source layout

```
app/main.py                 FastAPI routes, file validation, privacy safeguards
app/youcam.py               Official API integration (file, PUT, task, status)
static/index.html           Accessible page shell and SVG icon sprite
static/styles.css           Base interface styling
static/atelier.css            Refined editorial visual system, responsive states, accessibility
static/skin-study.svg         Original line-art visual for the hero
static/app.js               Screen navigation, results, routine engine, journaling
static/favicon.svg          Original app icon
screenshots/                Real captures of the running prototype
screenshots/capture_screenshots.py  Optional screenshot generation
pytest.ini / tests/         Core regression and mocked YouCam workflow tests
docs/DEVPOST_SUBMISSION.md  Submission description and captions
docs/DEMO_VIDEO_SCRIPT.md   2:15-minute own-voice demo guide
.env.example                Configuration template
```

## Verify

```bash
python -m pytest -q
```

> Test uses `httpx.MockTransport` to exercise the real upload/task/poll orchestration without calling or charging YouCam.

## Security / data notes

- Never expose API key to the browser: it is read server-side from `.env`.
- Original selfie files are **not** stored on the Serein server; the backend re-encodes in memory to strip metadata before forwarding to YouCam. The browser preview disappears after the scan. Photo transfer in live mode is to YouCam according to its privacy/retention policies.
- Only scores, source (`sample`/`youcam-live`), check-in date, and text reflection are stored in the user's browser via `localStorage` (limited to 25 snapshots).
- Third-party pre-signed upload URLs must be HTTPS and use trusted object storage hostnames to reduce SSRF risk.
- The app is a hackathon prototype, not a clinical device or production-hardened multi-tenant service.
- Local journal can be deleted in Skin Journal. Clearing browser storage also clears it.
- Cookie-free; no login, analytics trackers, face recognition, or medical diagnosis. (Optional remote Google Fonts are loaded by CSS; these do not include uploaded photos.)

## Production / hosting note

Do not host as an internet-facing public service with your paid YouCam key until you add abuse prevention (authentication, user-level rate limits, quotas, CSRF strategy if cookies are introduced, and hosting security). API calls can consume billable units. A public deployment can use any Python ASGI host with HTTPS (e.g. Render) and an environment variable for the key.

## Hackathon submission

The Devpost rules request a source repo URL, description, screenshots, and a publicly viewable 1–3-minute video. See `docs/DEVPOST_SUBMISSION.md` and `docs/DEMO_VIDEO_SCRIPT.md`.

Serein is an independent prototype using Perfect Corp's documented APIs; it is not an official Perfect Corp product.

### One-click Windows start

Extract the zip, double-click **SETUP_WINDOWS.bat** once and then **START_WINDOWS.bat**. The local browser opens at `http://127.0.0.1:8011`. The batch files prefer the global Python 3.12 at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` and fall back to `python`.

### Capturing the five real screenshots on your machine

With the server running, open a second terminal and run:

```powershell
pip install playwright
python -m playwright install chromium
python screenshots/capture_screenshots.py
```

The script captures every screen, including the explicitly labelled sample outputs. You can also use **Win+Shift+S** in the browser. For Devpost, provide screenshots of what is actually running, not concept renders.


## Live YouCam setup (v1.4)

1. Get your own YouCam API Bearer token from your YouCam developer account. Hackathon promo units are not the token; redeeming credits does not authenticate API requests.
2. Run `CONNECT_YOUCAM_WINDOWS.bat`. It requests the token using a hidden PowerShell input and saves it locally in `.env`, which `.gitignore` excludes from GitHub.
3. Restart `START_WINDOWS.bat` and visit http://127.0.0.1:8011. The app will say **API key loaded · Scan to verify**. This only means a token was configured, not that authentication succeeded.
4. Upload a permitted real, front-facing portrait, check the consent box, and press **Analyse my skin**. Only after a scan succeeds will the label say **YouCam scan verified**.

Do not make Devpost claims that a live YouCam API request succeeded until it actually does. Screenshots in `screenshots/` contain real interface renders but illustrative, clearly labelled scores for Insights/Ritual/Journal.
