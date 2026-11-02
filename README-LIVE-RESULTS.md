# Authentic YouCam screenshots (not sample screenshots)

This release intentionally includes **no claimed YouCam-result screenshots** because
we did not have a working user API key or network access to validate the provider
here. We will not disguise sample UI as a real API result.

To produce real screenshots on your Windows PC:

1. Install the project via `SETUP_WINDOWS.bat`.
2. Get a YouCam developer API key at <https://yce.perfectcorp.com/ai-api>.
   Your hackathon redeem code gives you units, it is **not** the API key.
3. Run `CONNECT_YOUCAM_WINDOWS.bat` to store the token locally in `.env`.
4. Run `START_WINDOWS.bat` and keep its terminal open. Server must be on port `8011`.
5. Get your own clear, front-facing JPG/PNG photo (minimum 480 px short side).
6. Run `CAPTURE_LIVE_WINDOWS.bat`, paste the photo path, and explicitly give consent.
7. The browser will make a **genuine** YouCam scan using your local backend and only
   after success save five 1500×1000 PNGs in `LIVE_YOUCAM_SCREENSHOTS/`.

If the scan fails, screenshots are not generated. The script does not fake scores,
substitute its own results or capture API-key screenshots. Use the `VERIFICATION.json`
file to confirm that the source was `youcam-live`.

## Privacy and access

Your YouCam API key is stored only in the local `.env` and must never be committed.
A live scan sends your portrait to YouCam with your consent. The portrait is not
stored by the server, but the screenshot automation can include personal cosmetic
insights, so review images before publishing them. `LIVE_YOUCAM_SCREENSHOTS/` is
excluded from Git by default. Do not publish the verification report if you do
not want its timestamp disclosed.

## Limits

API authentication/processing could not be validated from the assistant's isolated
sandbox. **No live scan has been performed by the assistant.**
