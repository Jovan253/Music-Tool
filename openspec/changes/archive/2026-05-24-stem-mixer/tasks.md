## 1. Backend — Stem Serving Route

- [x] 1.1 Create `apps/api/routes/stems.py` — `GET /jobs/{job_id}/stems/{stem_name}` endpoint: validate stem name, look up job, return `FileResponse` for the wav path from `job.stems`, 404 on unknown job / not-done / invalid stem name
- [x] 1.2 Register the stems router in `apps/api/main.py`
- [x] 1.3 Smoke-test: upload a file, wait for done, hit `GET /jobs/{job_id}/stems/vocals` in browser and confirm wav plays

## 2. Frontend — Dependencies & Polling

- [x] 2.1 Add `wavesurfer.js` to `apps/web/package.json` and install
- [x] 2.2 Add `getJobStatus(jobId)` to `apps/web/src/lib/api.ts` — `GET /jobs/{job_id}` returning the full job response including `stems`
- [x] 2.3 Update `UploadZone.tsx` — after 201 response, enter polling state: call `getJobStatus` every 3 s, show a "Separating stems…" loading indicator, on `done` pass job data up, on `failed` show error with retry

## 3. Frontend — Waveform Component

- [x] 3.1 Create `apps/web/src/features/waveform/Waveform.tsx` — wraps a WaveSurfer instance; accepts `audioUrl` and `wavesurfer` ref props; renders the waveform container div and initializes WaveSurfer on mount

## 4. Frontend — Stem Mixer

- [x] 4.1 Create `apps/web/src/features/mixer/TrackRow.tsx` — single stem row: stem label, `Waveform`, volume slider (0–1), mute button, solo button; accepts `stemName`, `audioUrl`, `volume`, `muted`, `soloed` props and callbacks
- [x] 4.2 Create `apps/web/src/features/mixer/StemMixer.tsx` — receives `jobId` and `stems` dict; creates one WaveSurfer MultiTrack instance; renders 4 `TrackRow` components; owns `volume`, `muted`, `soloedTrack` state; wires play/pause/seek transport controls
- [x] 4.3 Wire `StemMixer` into `App.tsx` — when `UploadZone` signals `done`, render `<StemMixer jobId={...} stems={...} />` in place of the upload zone

## 5. Verification

- [x] 5.1 Start both servers, upload an mp3, confirm the UI transitions through: upload progress → "Separating stems…" → mixer with 4 waveforms
- [x] 5.2 Confirm play/pause syncs all 4 tracks with no audible drift
- [x] 5.3 Confirm volume slider adjusts individual track level
- [x] 5.4 Confirm mute silences a track while others continue
- [x] 5.5 Confirm solo silences all other tracks; disabling solo restores them
