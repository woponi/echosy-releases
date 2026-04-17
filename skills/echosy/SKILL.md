---
name: echosy
description: Interact with the Echosy transcription app via its local API or read .echo transcript files offline. Also exposes Echosy's on-device LLM (Gemma 4 / Qwen 3.5) for ad-hoc prompt interactions.
argument-hint: "[list | latest | transcript <name> | search <keyword> | summary <name> | ask <prompt>]"
allowed-tools: Bash, WebFetch
---

# Echosy Skill

Interact with the [Echosy](https://echosy.app) transcription app — read transcripts, control recordings, and search meeting notes.

## Quick Start

Echosy runs a local API on `http://127.0.0.1:8765` when the app is open.

```bash
# Check if Echosy is running
curl -sf http://127.0.0.1:8765/api/status

# List all recordings
curl -s http://127.0.0.1:8765/api/recordings

# Get the latest transcript
LATEST=$(curl -s http://127.0.0.1:8765/api/recordings | python3 -c "
import sys,json
recs=json.load(sys.stdin)
recs.sort(key=lambda r:r.get('modified',0), reverse=True)
print(recs[0]['name'] if recs else '')
" 2>/dev/null)
curl -s "http://127.0.0.1:8765/api/recordings/${LATEST}/transcript"
```

---

## API Reference

All endpoints are on `http://127.0.0.1:8765` (localhost only).

### Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | App status — recording state, model loaded, chunk progress |

### Recordings & Transcripts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recordings` | List all recordings |
| GET | `/api/recordings/{name}/transcript` | Get transcript (markdown + JSON segments) |
| GET | `/api/recordings/{name}/summary` | Get summary markdown |
| PUT | `/api/recordings/{name}/transcript` | Save/update transcript |
| POST | `/api/recordings/{name}/rename` | Rename recording — body: `{"new_name": "..."}` |
| PUT | `/api/recordings/{name}/subject` | Update subject — body: `{"subject": "..."}` |
| DELETE | `/api/recordings/{name}` | Delete recording |
| POST | `/api/export` | Export transcript — body: `{"name": "...", "format": "md\|txt\|srt\|vtt"}` |

**List response:**
```json
[{"name": "recording_2026-03-29_14-30-00", "has_transcript": true, "has_summary": false, "duration": 1234.5, "modified": 1711700000, "segment_count": 42}]
```

**Transcript response:**
```json
{
  "content": "**[00:00:01 → 00:00:05]** Hello...",
  "decorated_content": "...",
  "segments": [{"id": 1, "text": "Hello", "startTime": 1, "endTime": 5, "source": "recording"}]
}
```

### Recording Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recording/start` | Start — body: `{"capture_mic": true, "save_wav": true}` |
| POST | `/api/recording/stop` | Stop recording |
| POST | `/api/recording/toggle` | Toggle recording on/off |
| POST | `/api/recording/mic` | Toggle mic — body: `{"capture_mic": true}` |
| POST | `/api/recording/retranscribe` | Re-run transcription — body: `{"name": "..."}` |
| POST | `/api/recording/retranscribe/cancel` | Cancel retranscribe |

### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/summary/generate` | Generate summary — body: `{"text": "...", "filename": "..."}` |
| POST | `/api/summary/stop` | Stop summary generation |
| POST | `/api/chat/send` | Chat about transcript (streams over WebSocket) — body: `{"messages": [...], "context": "...", "session": "transcript"}` |
| POST | `/api/decorate` | Translate/punctuate — body: `{"segments": [...], "mode": "translate", "target_language": "English"}` |
| POST | `/api/decorate/stop` | Stop decoration |

### Local LLM (Echosy Internal) — on-device Gemma 4 / Qwen 3.5

The on-device LLM runs in its own sidecar process and can be driven directly
for arbitrary prompt interactions — summaries, rewrites, translations,
extraction, brainstorming, etc. Synchronous (no WebSocket needed).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/local-llm/models` | List available + downloaded local models |
| POST | `/api/local-llm/test` | Quick round-trip sanity check (returns "OK") |
| POST | `/api/local-llm/generate` | **Run a prompt through the local LLM** |

**Generate endpoint body** — supply either a simple `prompt` (with optional `system`) or a full `messages` list, plus optional sampling params:

```json
{
  "prompt": "Summarise this meeting in three bullet points: ...",
  "system": "You are a concise note-taker.",
  "max_tokens": 512,
  "temperature": 0.4
}
```

Or with an explicit conversation:

```json
{
  "messages": [
    {"role": "system", "content": "Reply in Traditional Chinese."},
    {"role": "user", "content": "What is mlx-lm?"}
  ],
  "max_tokens": 300,
  "temperature": 0.6
}
```

**Response:**
```json
{"ok": true, "model_id": "gemma-4-e4b", "response": "..."}
```

Notes:
- Requires a local model to be selected in Echosy settings (`llm_local_model`).
- The model is loaded on first call and stays resident until idle-unload fires (default 10 min) or RAM pressure.
- Call is blocking — expect a few seconds for short replies, longer for bigger contexts.
- `max_tokens` is clamped to `[1, 8192]`; `temperature` to `[0.0, 2.0]`.
- 400 if no model selected, 503 if the local LLM engine is unavailable, 500 on generation error.

**Quick examples:**

```bash
# Simple one-shot prompt
curl -s http://127.0.0.1:8765/api/local-llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Give me three startup name ideas for a meeting transcription app."}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"

# Summarise the latest Echosy transcript with the local model
LATEST=$(curl -s http://127.0.0.1:8765/api/recordings \
  | python3 -c "import sys,json; r=json.load(sys.stdin); r.sort(key=lambda x:x.get('modified_at',0),reverse=True); print(r[0]['name'])")
TRANSCRIPT=$(curl -s "http://127.0.0.1:8765/api/recordings/${LATEST}/transcript" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('content',''))")
python3 -c "
import json,sys,urllib.request
body=json.dumps({'system':'You are a concise meeting summariser. Output markdown bullets.',
                 'prompt':sys.argv[1],'max_tokens':600,'temperature':0.3}).encode()
req=urllib.request.Request('http://127.0.0.1:8765/api/local-llm/generate',
                           data=body, headers={'Content-Type':'application/json'})
print(json.loads(urllib.request.urlopen(req).read())['response'])
" "$TRANSCRIPT"

# Multi-turn conversation
curl -s http://127.0.0.1:8765/api/local-llm/generate \
  -H "Content-Type: application/json" \
  -d '{"messages":[
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":"Translate to Japanese: The meeting starts at 10am."}
      ]}'
```

**When to use which LLM endpoint:**
- `/api/local-llm/generate` — ad-hoc prompts, rewrites, translation, extraction. Synchronous, no session/context persistence. Use this whenever you just need the model to answer something.
- `/api/chat/send` — only when you want the response streamed over WebSocket with session tracking (e.g. when driving the Ask AI panel from code). For plain prompting, prefer the generate endpoint.

### File/URL Transcription

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/files/transcribe` | Transcribe file — body: `{"path": "/path/to/file.mp4"}` |
| POST | `/api/files/transcribe-url` | Transcribe URL — body: `{"url": "https://..."}` |
| POST | `/api/files/stop` | Stop file transcription |

### ASR Models

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/asr/languages` | List supported languages |
| GET | `/api/asr/models` | List available/downloaded models |
| POST | `/api/asr/download` | Download model — body: `{"model_id": "..."}` |
| POST | `/api/asr/delete` | Delete model — body: `{"model_id": "..."}` |

### Dictation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/dictation/toggle` | Toggle dictation |
| POST | `/api/dictation/toggle-edit` | Toggle edit mode |
| GET | `/api/dictation/status` | Dictation status |
| GET | `/api/dictation/languages` | Available languages |
| GET | `/api/dictation/check-mic` | Check mic availability |
| GET | `/api/dictation/mic-devices` | List mic devices |

---

## Offline Usage

When Echosy is not running, you can read `.echo` files directly. They are ZIP archives containing `manifest.json`, `transcript.md`, `transcript.json`, and `audio.flac`.

```python
import zipfile, json

with zipfile.ZipFile("recording.echo", "r") as zf:
    manifest = json.loads(zf.read("manifest.json"))
    transcript = zf.read("transcript.md").decode("utf-8")
    segments = json.loads(zf.read("transcript.json"))
    print(f"Duration: {manifest.get('duration_seconds', 0):.0f}s")
    print(f"Segments: {len(segments)}")
    print(transcript)
```

## Notes

- API runs on **localhost only** — not exposed to the network
- Recording names may contain spaces — URL-encode them in URLs
- Transcripts may contain multilingual content (Chinese/English/Japanese/Korean)
- Some features have usage limits on the free tier (enforced server-side)
