# Echosy Plugin for Claude Code

Read, search, and summarize [Echosy](https://echosy.app) meeting transcripts (`.echo` files) directly from Claude Code.

## What is Echosy?

Echosy is a macOS app that captures system + microphone audio, transcribes it using on-device AI (Qwen3-ASR), and generates summaries. Recordings are saved as `.echo` files — ZIP archives containing transcripts, metadata, and audio.

## Installation

```bash
/plugin install echosy
```

## Usage

```bash
# List all transcripts in the project
/echosy list

# Read a transcript by keyword
/echosy transcript "standup"

# Search across all transcripts
/echosy search "budget"

# Get transcript with metadata header (for summarization)
/echosy summary "Q1 review"

# Show file info (duration, segments, date)
/echosy info "meeting"

# Get raw JSON segments with timestamps
/echosy json "interview"
```

## .echo File Format

`.echo` files are ZIP archives containing:

| File | Description |
|------|-------------|
| `manifest.json` | Metadata (date, duration, segment count, source) |
| `transcript.md` | Human-readable markdown transcript with timestamps |
| `transcript.json` | Machine-readable segments with precise start/end times |
| `audio.flac` | Audio recording (not read by this plugin) |

## File Resolution

The file argument supports flexible matching:
- **Full path**: `transcript/Meeting_2026-03-10.echo`
- **Filename**: `Meeting_2026-03-10.echo`
- **Keyword**: `Meeting` — matches against filenames in the transcript directory

## Configuration

Set `ECHOSY_TRANSCRIPT_DIR` environment variable to change the default transcript directory (defaults to `transcript/` in the project root).

## License

MIT
