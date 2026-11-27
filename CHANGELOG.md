# Release log

## 2.3.0 — 2026-11-28

- Improve transcription recovery, filter short noise and filler-only results, and clean AI context.
- Add Claude summaries/chat, transcript search and timestamp citations.
- Show recording titles, recording-path copying and History workspace totals.
- Restore the production trial to 30 minutes.

Source: [3ea08b3](https://github.com/woponi/Echosy/commit/3ea08b3) (release configuration), [eaa5e4b](https://github.com/woponi/Echosy/commit/eaa5e4b74758f1c1157416ce6e9adbb02ba438cf) (packaged application changes).

Artifact: [Echosy_2.3.0_aarch64.dmg](https://github.com/woponi/echosy-releases/releases/download/v2.3.0/Echosy_2.3.0_aarch64.dmg), 564115608 bytes.

SHA-256: `bf1373c8c0d8ea2d9ec85b4bbd5e81080ebeb8461352eb52f4b85aecd4b666de`.

Validation: 24 Python regression tests and frontend production build passed; final DMG app signature verified with `codesign --verify --deep --strict`; packaged VAD asset and 1800-second trial verified; packaged ASR model loaded with no error and generated speech was transcribed; interface and History rendered after relaunch. An initial blank window was observed before relaunch and was not reproduced afterward.

Apple notarization: Accepted, submission `3dd645b6-32ae-4a58-908a-1c57fddaa0ca`. Stapler validation and Gatekeeper assessment passed. Apple Silicon only; existing Intel installer remains unchanged.
