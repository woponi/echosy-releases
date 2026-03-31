---
name: echosy
description: Interact with the Echosy transcription app via its local API or read .echo transcript files offline.
argument-hint: "[list | latest | transcript <name> | search <keyword> | summary <name>]"
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
| POST | `/api/chat/send` | Chat about transcript — body: `{"message": "...", "context": "...", "session": "transcript"}` |
| POST | `/api/decorate` | Translate/punctuate — body: `{"segments": [...], "mode": "translate", "target_language": "English"}` |
| POST | `/api/decorate/stop` | Stop decoration |

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
