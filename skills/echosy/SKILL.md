---
name: echosy
description: Read Echosy meeting transcript files (.echo format). Use when the user wants to read, search, summarize, or list meeting transcripts.
argument-hint: "[list | transcript <file> | search <keyword> | summary <file>]"
allowed-tools: Bash
---

Read and search Echosy .echo meeting transcript files. These are ZIP archives containing audio + transcript data.

## Commands

```bash
# List all available transcripts
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py list

# Show file metadata (date, duration, segments)
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py info '<file_or_keyword>'

# Read the markdown transcript
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py transcript '<file_or_keyword>'

# Read transcript with metadata header (good for summarization)
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py summary '<file_or_keyword>'

# Get raw JSON segments (with precise timestamps)
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py json '<file_or_keyword>'

# Search keyword across all transcripts
python3 ${CLAUDE_SKILL_DIR}/scripts/echosy.py search '<keyword>'
```

## File Resolution

The `<file_or_keyword>` argument supports:
- Full path: `transcript/Meeting_2026-03-10_11-42-52.echo`
- Filename: `Meeting_2026-03-10_11-42-52.echo`
- Keyword match: `Meeting` (matches against filenames in transcript/ dir)

## Default Transcript Directory

Transcripts are stored in `transcript/` under the project root. Override with `ECHOSY_TRANSCRIPT_DIR` environment variable.

## Typical Workflows

1. **List transcripts** → pick one → **read transcript** → **summarize key points**
2. **Search keyword** across all meetings to find relevant discussions
3. **Read summary** format and ask Claude to extract action items, decisions, or key topics

## Notes
- .echo files are ZIP archives containing: manifest.json, transcript.md, transcript.json, audio.flac
- Audio files are NOT read (too large) — only text content is extracted
- Transcripts may be in Chinese/English mixed content
