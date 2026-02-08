# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

lidarr-youtube-downloader (lyd) is a Python CLI tool that integrates with Lidarr (music collection manager) to find missing tracks and automatically download them from YouTube, then tag them with proper metadata. It runs as a continuous daemon or one-shot via `--stop`.

## Build & Development Commands

```bash
# Install dependencies
pip3 install eyed3 youtube-search-python yt-dlp requests typer

# Install the package locally
pip install -e .

# Lint (Black formatter + Dockerfile hadolint)
make lint

# Run tests (pytest configured but no tests exist yet)
pytest

# Version bump (updates PKG-INFO, pyproject.toml, setup.py)
make bump

# Build and upload to PyPI
make upload

# Docker build
docker build -t lyd .
```

## Required Environment Variables

```bash
LIDARR_URL="http://127.0.0.1:8686"
LIDARR_API_KEY="your-api-key"
LIDARR_DB="/path/to/lidarr.db"
LIDARR_MUSIC_PATH="/music"
```

## CLI Entry Points

- `lyd` - Main application (`lidarr_youtube_downloader/lyd.py`)
- `lyd-unmapped` - Fix unmapped track files in Lidarr DB (`lidarr_youtube_downloader/lyd-unmapped.py`)

## Architecture

### Data Flow

1. Query Lidarr API for missing tracks (paginated, 50/page)
2. Search YouTube for each track using "Artist - Title"
3. Fuzzy match results using `SequenceMatcher` (threshold: 0.8)
4. Download audio with `yt-dlp` (MP3 extraction)
5. Tag MP3 with metadata using eyed3 (ffmpeg as fallback)
6. Insert/update records directly in Lidarr's SQLite database
7. Trigger Lidarr rescan via API
8. Sleep and repeat (or exit with `--stop`)

### Key Design Decisions

- **Direct SQLite access**: The app writes directly to Lidarr's SQLite DB (not just via API) to insert TrackFiles and update Track records.
- **Template-based output**: `lidarr_youtube_downloader/view/` contains text templates for formatted console output at each pipeline stage.
- **State tracking**: A "seen" file prevents re-processing tracks; a ".skip" file blacklists failed YouTube URLs.
- **Dual tagging**: eyed3 for ID3 tags with ffmpeg as fallback for robustness.
- **Signal handling**: SIGINT is caught to complete the current track before exiting gracefully.

### External System Dependencies

- **ffmpeg** - Audio conversion and metadata embedding
- **yt-dlp** - YouTube audio extraction
- **Lidarr instance** - API + direct SQLite DB access required

## Code Formatting

Uses **Black** for Python formatting. Run `make lint` before committing.
