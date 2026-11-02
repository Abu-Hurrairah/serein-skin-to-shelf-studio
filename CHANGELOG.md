## v1.5 - verified live screenshot capture

- Added one-click Windows capture of genuine YouCam analysis screenshots, guarded by real completion checks.
- No demo/sample image output is included in this release.
- API key is required; there is no mock authentication or fake score generation.

# Changelog

## 1.2 — Devpost preparation
- Enlarged the visible, signed footer: **Designed & Developed by Abu Hurrairah**.
- Switched the Windows launcher and local quick-start URLs to port **8011**, avoiding an old server still running on port 8000.
- Added a branded 3:2 Devpost thumbnail based on a genuine prototype screenshot.
- Added visible `SEREIN 1.2` version text for checking the running edition.
- No changes to API calls or processing logic.

# Serein — release notes

## 1.1 / Editorial Edition — November 2, 2026

**Project creator: Abu Hurrairah**

- Rebuilt the visual direction into an understated, credible skincare studio rather than a generic dashboard.
- Created an original illustrative skin-study asset; added a more purposeful homepage and direct demo call-to-action.
- Restyled all five pages with one consistent editorial design system (`static/atelier.css`).
- Added developer attribution to the footer, sidebar, about dialog, and metadata.
- Improved compact navigation, keyboard focus, reduced-motion settings, and aria-current page state.
- Added responsive browser-rendered sample screens for review.
- Clarified connection wording: configured API key does not by itself confirm successful provider processing.
- Retained original privacy, signed upload, consent, analysis polling and routine/journal workflows.

### Verification

Python unit tests and JavaScript syntax checks run successfully. Desktop and mobile sample-mode navigation was exercised with headless Chromium. Live YouCam API calls still require user-provided credentials and have not been independently tested.
