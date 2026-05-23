## Context

The backend produces 4 stem wav files at `uploads/<job_id>/stems/htdemucs/`. The frontend currently shows a raw job ID on upload success with no further interaction. This design connects those two ends: a polling mechanism that watches job status, and a WaveSurfer.js mixer that renders and controls the 4 stems once ready.

Synchronized multi-track playback is the core UX constraint — all 4 waveforms must start, pause, and seek together with zero drift.

## Goals / Non-Goals

**Goals:**
- Poll `GET /jobs/{job_id}` until `done`, then transition to mixer
- Render 4 synchronized waveforms via WaveSurfer.js
- Per-track mute, solo, and volume slider controls
- Backend endpoint to stream stem files to the browser
- Transition UploadZone success state into the mixer

**Non-Goals:**
- Export / mix-down (Phase 2, Task 5)
- Timeline scrubbing UI (just click-to-seek for MVP)
- Stem labels / icons beyond text names
- Keyboard shortcuts
- Mobile layout optimization

## Decisions

### 1. WaveSurfer.js for waveform rendering
WaveSurfer.js is already in the project tech stack and handles waveform drawing, playback, and seek natively. The `MultiTrack` plugin in WaveSurfer 7+ provides synchronized multi-track playback with a single master transport — this is the right primitive to avoid drift. Alternative (Tone.js players with manual sync) is more complex and drift-prone.

### 2. Backend stem streaming route
The browser needs to fetch stem audio. Options:
- **Serve via new FastAPI route** `GET /jobs/{job_id}/stems/{stem_name}` using `FileResponse` — simple, no new infrastructure, works for local prototype.
- Serve via static files mount — would expose the entire uploads directory, not acceptable.
- Cloud storage presigned URLs — correct for production (Phase 3) but overkill now.

Using `FileResponse` for MVP. Path resolves from the job's `stems` dict, so the route never constructs file paths from user input directly.

### 3. Polling in the upload flow
After upload, `UploadZone` enters a polling state — it calls `GET /jobs/{job_id}` every 3 seconds until `status` is `done` or `failed`. On `done`, it hands `jobId` to the `StemMixer` component. On `failed`, it shows the error. This keeps the component tree simple: UploadZone owns the pre-mixer state; StemMixer owns the post-mixer state.

### 4. Component structure
```
features/
  upload/
    UploadZone.tsx       (existing — adds polling + transition)
  mixer/
    StemMixer.tsx        (top-level mixer: loads stems, owns transport)
    TrackRow.tsx         (single stem row: waveform + controls)
  waveform/
    Waveform.tsx         (WaveSurfer.js instance wrapper)
```
`StemMixer` creates one WaveSurfer MultiTrack instance and passes per-track refs down to `TrackRow`. Volume/mute/solo are local state in `StemMixer`, applied via the WaveSurfer API.

### 5. Solo behaviour
Solo = mute all other tracks. Implemented in `StemMixer` state: `soloedTrack: string | null`. When set, all other tracks get `setVolume(0)` and the soloed track gets its slider volume restored. No extra backend involvement.

## Risks / Trade-offs

- **WaveSurfer MultiTrack plugin API stability** — WaveSurfer 7 is relatively new. If MultiTrack has gaps, fallback is 4 independent WaveSurfer instances with `sync` via a shared `audioContext` and `AudioWorklet`. More complex but guaranteed sync.
- **Large wav files over local HTTP** — htdemucs outputs ~30–100MB wav per stem for a 3-min song. `FileResponse` streams fine locally; this becomes a real bottleneck in production (Phase 3 fix: S3 presigned URLs).
- **Polling interval vs. responsiveness** — 3s polling means up to 3s delay between job completing and UI updating. Acceptable for MVP; Phase 3 replaces with SSE or WebSocket.
