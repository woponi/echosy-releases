#!/usr/bin/env python3
"""Read .echo transcript files (Echosy app format).

.echo files are ZIP archives containing:
  - manifest.json  — metadata (created_at, segment_count, source, duration, etc.)
  - transcript.md  — human-readable markdown transcript with timestamps
  - transcript.json — machine-readable segments [{id, text, startTime, endTime, source}, ...]
  - audio.flac     — audio recording (skipped)
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import timedelta
from glob import glob
from pathlib import Path


TRANSCRIPT_DIR = os.environ.get("ECHOSY_TRANSCRIPT_DIR", "transcript")


def format_duration(seconds):
    """Format seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds == 0:
        return "unknown"
    td = timedelta(seconds=int(seconds))
    total = int(td.total_seconds())
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def resolve_echo_file(path_or_keyword):
    """Resolve a .echo file path — supports full path, filename, or keyword search."""
    # Direct path
    if os.path.isfile(path_or_keyword):
        return path_or_keyword

    # Try in transcript dir
    candidate = os.path.join(TRANSCRIPT_DIR, path_or_keyword)
    if os.path.isfile(candidate):
        return candidate

    # Add .echo extension
    if not path_or_keyword.endswith(".echo"):
        candidate = os.path.join(TRANSCRIPT_DIR, path_or_keyword + ".echo")
        if os.path.isfile(candidate):
            return candidate

    # Keyword search in transcript dir
    pattern = os.path.join(TRANSCRIPT_DIR, "*.echo")
    matches = []
    keyword_lower = path_or_keyword.lower()
    for f in sorted(glob(pattern)):
        if keyword_lower in os.path.basename(f).lower():
            matches.append(f)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple matches for '{path_or_keyword}':")
        for m in matches:
            print(f"  - {os.path.basename(m)}")
        print("\nPlease be more specific.")
        sys.exit(1)

    # Try recursive glob
    pattern = os.path.join("**", "*.echo")
    for f in sorted(glob(pattern, recursive=True)):
        if keyword_lower in os.path.basename(f).lower():
            matches.append(f)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple matches for '{path_or_keyword}':")
        for m in matches:
            print(f"  - {m}")
        print("\nPlease be more specific.")
        sys.exit(1)

    print(f"Error: No .echo file found for '{path_or_keyword}'")
    sys.exit(1)


def read_echo(path):
    """Read all text contents from a .echo file."""
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()

        manifest = json.loads(zf.read("manifest.json")) if "manifest.json" in names else {}

        if "transcript.md" in names:
            transcript_md = zf.read("transcript.md").decode("utf-8")
        elif "summary.md" in names:
            transcript_md = zf.read("summary.md").decode("utf-8")
        else:
            transcript_md = "(no transcript found)"

        transcript_json = json.loads(zf.read("transcript.json")) if "transcript.json" in names else []

    return manifest, transcript_md, transcript_json


def cmd_info(args):
    """Show metadata for a .echo file."""
    path = resolve_echo_file(args.file)
    manifest, _, segments = read_echo(path)

    # Calculate duration from segments if manifest doesn't have it
    duration = manifest.get("duration_seconds", 0)
    if (not duration or duration == 0) and segments:
        duration = max(s.get("endTime", 0) for s in segments)

    print(f"File:       {os.path.basename(path)}")
    print(f"Created:    {manifest.get('created_at', 'unknown')}")
    print(f"Source:     {manifest.get('source', 'unknown')}")
    print(f"Segments:   {manifest.get('segment_count', len(segments))}")
    print(f"Duration:   {format_duration(duration)}")
    print(f"Audio:      {manifest.get('audio_format', 'unknown')}")
    print(f"Version:    {manifest.get('version', 'unknown')}")


def cmd_transcript(args):
    """Output the markdown transcript."""
    path = resolve_echo_file(args.file)
    _, transcript_md, _ = read_echo(path)
    print(transcript_md)


def cmd_json(args):
    """Output the JSON transcript segments."""
    path = resolve_echo_file(args.file)
    _, _, segments = read_echo(path)
    print(json.dumps(segments, ensure_ascii=False, indent=2))


def cmd_search(args):
    """Search for keywords in transcripts."""
    keyword = args.keyword.lower()
    search_dir = args.dir or TRANSCRIPT_DIR

    pattern = os.path.join(search_dir, "*.echo")
    files = sorted(glob(pattern))

    if not files:
        # Try recursive
        pattern = os.path.join("**", "*.echo")
        files = sorted(glob(pattern, recursive=True))

    found = False
    for f in files:
        try:
            _, transcript_md, _ = read_echo(f)
            lines = transcript_md.split("\n")
            matches = [l for l in lines if keyword in l.lower()]
            if matches:
                if not found:
                    found = True
                print(f"\n📄 {os.path.basename(f)}")
                for m in matches:
                    print(f"  {m.strip()}")
        except Exception:
            continue

    if not found:
        print(f"No matches found for '{args.keyword}'")


def cmd_list(args):
    """List all .echo files."""
    search_dir = args.dir or TRANSCRIPT_DIR
    pattern = os.path.join(search_dir, "*.echo")
    files = sorted(glob(pattern))

    if not files:
        print(f"No .echo files found in {search_dir}/")
        return

    print(f"Found {len(files)} transcript(s) in {search_dir}/:\n")
    for f in files:
        try:
            manifest, _, segments = read_echo(f)
            duration = manifest.get("duration_seconds", 0)
            if (not duration or duration == 0) and segments:
                duration = max(s.get("endTime", 0) for s in segments)
            name = os.path.basename(f).replace(".echo", "")
            seg_count = manifest.get("segment_count", len(segments))
            print(f"  {name}  ({format_duration(duration)}, {seg_count} segments)")
        except Exception:
            print(f"  {os.path.basename(f)}  (error reading)")


def cmd_summary(args):
    """Output transcript with metadata header for summarization."""
    path = resolve_echo_file(args.file)
    manifest, transcript_md, segments = read_echo(path)

    duration = manifest.get("duration_seconds", 0)
    if (not duration or duration == 0) and segments:
        duration = max(s.get("endTime", 0) for s in segments)

    name = os.path.basename(path).replace(".echo", "")
    print(f"# Meeting Transcript: {name}")
    print(f"- **Date:** {manifest.get('created_at', 'unknown')}")
    print(f"- **Duration:** {format_duration(duration)}")
    print(f"- **Segments:** {manifest.get('segment_count', len(segments))}")
    print(f"\n---\n")
    print(transcript_md)


def main():
    parser = argparse.ArgumentParser(description="Read Echosy .echo transcript files")
    sub = parser.add_subparsers(dest="command", help="Command")

    # list
    p_list = sub.add_parser("list", help="List all .echo files")
    p_list.add_argument("--dir", help="Directory to search", default=None)

    # info
    p_info = sub.add_parser("info", help="Show file metadata")
    p_info.add_argument("file", help="Path, filename, or keyword")

    # transcript
    p_trans = sub.add_parser("transcript", help="Output markdown transcript")
    p_trans.add_argument("file", help="Path, filename, or keyword")

    # json
    p_json = sub.add_parser("json", help="Output JSON segments")
    p_json.add_argument("file", help="Path, filename, or keyword")

    # summary
    p_summary = sub.add_parser("summary", help="Output transcript with metadata for summarization")
    p_summary.add_argument("file", help="Path, filename, or keyword")

    # search
    p_search = sub.add_parser("search", help="Search keyword across all transcripts")
    p_search.add_argument("keyword", help="Keyword to search for")
    p_search.add_argument("--dir", help="Directory to search", default=None)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "list": cmd_list,
        "info": cmd_info,
        "transcript": cmd_transcript,
        "json": cmd_json,
        "summary": cmd_summary,
        "search": cmd_search,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
