## Context

The mixer has per-stem volume and mute controls, but there's no way to save the result. This change adds a synchronous server-side mix-down: the frontend POSTs the current mix settings, the backend loads the 4 stem wavs, applies per-stem gain/muting via pydub, overlays them, and streams back a single audio file.

ffmpeg is already available on the machine (Demucs requires it). pydub is a thin Python wrapper around ffmpeg that makes audio manipulation trivial.

## Goals / Non-Goals

**Goals:**
- `POST /jobs/{job_id}/export` — accepts `{ stems: { vocals: 0.8, drums: 0.0, bass: 1.0, other: 1.0 }, format: "mp3" | "wav" }`, returns audio file as download
- Export button in the mixer UI that captures current volumes/mutes and triggers browser download
- mp3 (192kbps) and wav (source quality) format support

**Non-Goals:**
- Async export job / progress indicator — mix-down is fast (< 5s), blocking response is fine for MVP
- Client-side rendering via Web Audio API — adds complexity with no benefit given we already have wavs server-side
- Saving exports / download history — one-shot per request
- Bitrate or sample rate control

## Decisions

### 1. Server-side mix-down with pydub
pydub overlays audio segments with volume adjustments in pure Python (delegating encoding to ffmpeg). The API is simple: `audio.apply_gain(db)` and `audio.overlay(other)`. This is the right choice over:
- **ffmpeg subprocess directly**: more complex filter graph construction for N tracks
- **librosa/soundfile**: good for analysis, not mixing
- **Client-side Web Audio**: requires streaming all 4 wavs to the browser, then re-uploading the result — wasteful

### 2. Volume as a linear 0–1 scalar, converted to dB on the backend
The frontend already uses 0–1 volume values (WaveSurfer's `setVolume` API). The backend converts to dB: `gain_db = 20 * log10(volume)` (with `volume=0` treated as `-inf`, i.e. silence). This avoids floating-point edge cases and keeps the API intuitive.

### 3. Synchronous response with StreamingResponse
Mix-down takes < 5s even for a 5-minute song on CPU. A synchronous `StreamingResponse` (piping the pydub output to the response body) avoids temp file management and keeps the implementation simple. No need for a job queue at this scale.

### 4. Temp file for encoding
pydub needs to write to a file or buffer to encode mp3 (requires ffmpeg). We write to a `tempfile.NamedTemporaryFile`, stream it in the response, then delete it. This is safe and avoids accumulating export files on disk.

## Risks / Trade-offs

- **Large wavs → slow mix on CPU** — htdemucs wav output for a 4-min song is ~100MB total. pydub loads all 4 into memory. On a low-memory server this could fail. Mitigation: 50MB upload limit already caps input length; stem wavs are proportional.
- **pydub mp3 encoding requires ffmpeg** — if ffmpeg isn't in PATH, mp3 export fails. Mitigation: Demucs already requires ffmpeg, so it's guaranteed present in our environment.
- **Concurrent exports** — multiple users exporting simultaneously will multiply memory usage. Non-issue for local prototype; Phase 3 (cloud deploy) will need limits.
