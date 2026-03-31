# Echosy Plugin for Claude Code

Interact with the [Echosy](https://echosy.app) transcription app — read transcripts, control recordings, search meeting notes, and use AI features via the local API.

## What is Echosy?

Echosy is a macOS app that captures system + microphone audio, transcribes it using on-device AI (Qwen3-ASR), and generates summaries. Recordings are saved as `.echo` files — ZIP archives containing transcripts, metadata, and audio.

## Installation

```bash
/plugin install echosy
```

Or add the marketplace first:

```bash
/plugin marketplace add woponi/echosy-releases
/plugin install echosy@woponi/echosy-releases
```

## Usage

### Live API (when Echosy app is running)

```bash
# Get the latest transcript
/echosy latest

# List all recordings
/echosy list

# Read a specific transcript
/echosy transcript "standup"

# Search across all transcripts
/echosy search "budget"
```

The plugin auto-detects if Echosy is running on `localhost:8765` and uses the live API for richer data including recording control, AI summaries, and real-time status.

### Offline (read .echo files directly)

```bash
# Get transcript with metadata header (for summarization)
/echosy summary "Q1 review"

# Show file info (duration, segments, date)
/echosy info "meeting"

# Get raw JSON segments with timestamps
/echosy json "interview"
```

## Live API Capabilities

When Echosy is running, the plugin can:

- **List & read** recordings, transcripts, and summaries
- **Control recording** — start, stop, toggle mic
- **AI features** — generate summaries, chat about transcripts, translate/punctuate
- **File transcription** — transcribe audio/video files or URLs
- **Re-transcribe** — re-run segmentation with different VAD settings

## .echo File Format

`.echo` files are ZIP archives containing:

| File | Description |
|------|-------------|
| `manifest.json` | Metadata (date, duration, segment count, source) |
| `transcript.md` | Human-readable markdown transcript with timestamps |
| `transcript.json` | Machine-readable segments with precise start/end times |
| `audio.flac` | Audio recording (not read by this plugin) |

## Configuration

Set `ECHOSY_TRANSCRIPT_DIR` environment variable to change the default transcript directory (defaults to `transcript/` in the project root).

## License

MIT
