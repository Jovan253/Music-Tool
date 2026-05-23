## Why

The backend now produces 4 stem files (vocals, drums, bass, other) but the frontend has no way to play them. This change connects the output of Demucs to a usable multi-track mixer UI — the first moment the product actually does what it promises.

This is Phase 2, Task 4.

## What Changes

- New `apps/web/src/features/mixer/` — multi-track mixer component that polls `GET /jobs/{job_id}` until `done`, then renders 4 waveforms and per-track controls
- New `apps/web/src/features/waveform/` — WaveSurfer.js waveform component wrapper
- New `GET /jobs/{job_id}/stems/{stem_name}` backend route — serves stem wav files as audio so the browser can stream them
- `UploadZone` updated — transitions to the mixer view on job completion rather than showing a plain success message
- WaveSurfer.js added to frontend dependencies

## Capabilities

### New Capabilities

- `stem-mixer`: Multi-track waveform player with per-stem mute, solo, and volume controls. All 4 tracks play synchronized. Powered by WaveSurfer.js.

### Modified Capabilities

- `audio-upload`: Upload flow now transitions to the mixer on job completion — the success state is the mixer, not a static message.

## Impact

- New frontend dependency: `wavesurfer.js`
- New backend route: `GET /jobs/{job_id}/stems/{stem_name}` — reads stem wav from `uploads/<job_id>/stems/` and streams it
- `UploadZone.tsx` modified — adds polling loop and passes job data to mixer on completion
- No changes to job store, separation worker, or existing API contracts
- No new backend dependencies
