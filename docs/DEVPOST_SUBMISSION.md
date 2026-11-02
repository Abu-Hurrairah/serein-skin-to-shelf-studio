# Devpost submission material — Serein

**Creator / Developer:** Abu Hurrairah

## Project title
Serein — The Skin-to-Shelf Studio

## Tagline
Your skin, your signals, your smarter shopping list.

## Inspiration
Skincare shoppers can face a paradox of choice: endless recommendations, conflicting ingredient trends, and little clarity on what their skin actually needs. A scan without a next step isn't enough. Serein helps connect visible skin signals to a small, explainable set of shopping decisions, including products you can skip.

## What it does
Serein transforms a photo-based YouCam Skin Analysis v2.1 result into a practical cosmetic routine. A visitor can upload or capture a front-facing portrait, consent to processing, and inspect the actual returned appearance indicators. The app then ranks areas to focus on, proposes a lightweight morning/evening routine, and creates an intentionally small category-level shopping basket. Visitors can add/remove optional items, change an illustrative budget tier, and save reflections in a local-only skin journal.

A clearly labeled illustrative sample mode allows judges to explore the complete decision-making experience without spending API credits. It does not claim to be actual YouCam analysis.

## How we built it
- **Frontend:** responsive HTML, modern CSS, and zero-framework JavaScript for a low-friction interface.
- **Backend:** FastAPI, HTTPX, Pillow, and the officially documented YouCam Skin Analysis v2.1 endpoints.
- **Real integration:** File API creates a signed upload slot; backend PUTs the actual portrait; a v2.1 skin-analysis task is created with six SD features; frontend polls task status and displays only real returned scores.
- **Decision engine:** interpretable rules prioritise low-scoring appearance metrics and cap suggested optional categories at two. No opaque recommendation API and no invented products.
- **Privacy:** image metadata is removed by JPEG re-encoding; image bytes are not written to local disk; journal retains only scores and notes in localStorage.

## Challenges
Balancing a rich retail experience with genuine transparency: scores should not be described as medical diagnoses, sample data must not masquerade as analysis, and shoppers should be able to understand *why* an item appears in their routine. We kept the decision engine and its assumptions accessible in the source code.

## What we learned
Designing a useful downstream product from asynchronous AI results requires more than forwarding a score. The YouCam integration involves signed file uploads, separate task creation, and polling for completion. Mapping those outputs to an intentionally small routine made the product's consumer value tangible.

## What's next
With consent and production review: localized ingredient catalogs, real merchant catalog partnerships, multiple visit comparisons, internationalization, and privacy-focused user accounts. Estimated example prices currently are not live retail prices.

## Design and development
Designed and developed by **Abu Hurrairah**. The custom editorial visual system, independent interaction logic, analysis mapping, and application backend are included in the source repository.

## Built with
YouCam Skin Analysis API v2.1, FastAPI, Python, HTTPX, Pillow, HTML, CSS, JavaScript.

## Links to fill before submission
- Source repository URL: [ADD YOUR PUBLIC GITHUB REPO URL]
- Live demo URL: [ADD URL IF HOSTED; LOCAL DEMO STEPS IN README]
- Demo video URL (public 1–3 min): [ADD YOUR YOUTUBE URL]

## Screenshot captions
1. **Overview:** Serein positions the skin scan as the start of an intentional shopping journey.
2. **Scan:** photo upload, camera option, consent, and a clearly separate sample journey.
3. **Insights:** a readable snapshot of individual appearance scores and the most relevant concerns.
4. **Ritual:** balanced AM/PM plan and the explained, capped category-level basket.
5. **Journal:** local-only tracking and user reflections over multiple sessions.

## Important truth-in-demo checklist
- Do not describe sample results as live YouCam findings.
- For a true live API demonstration, obtain your own API key and run a real photo through the flow.
- Do not say this app diagnoses skin disorders or prescribes medical care.
- Do not state that this app has been deployed or integrated with real merchants.
- Publish GitHub code and a public YouTube demo yourself before the Devpost deadline.
