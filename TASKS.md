# Music Tool — Project Tasks

High-level roadmap. Each item links to its OpenSpec change or notes the current status.
Detailed per-change tasks live in `openspec/changes/<name>/tasks.md`.

---

## Phase 1 — Local Prototype

- [x] Monorepo setup — React + TypeScript frontend, FastAPI backend, shared env config (`monorepo-setup`)
- [x] Audio upload — drag-and-drop UI, `POST /upload`, in-memory job store, `GET /jobs/{job_id}` (`audio-upload`)
- [x] Demucs worker — stem separation wired to upload, job status polling (`demucs-worker`)

## Phase 2 — Basic Web App

- [x] Stem mixer — multi-track waveform playback (WaveSurfer.js), mute/solo/volume per stem
- [x] Export — render and download a custom mix as mp3 or wav

## Phase 3 — Production Infrastructure

- [x] Async job queue — replace daemon thread with Redis + Celery (or RQ); add job progress events
- [x] Cloud storage — move uploads and stems to Supabase Storage or S3; presigned URLs for playback
- [x] Database — PostgreSQL job/user records via SQLAlchemy; migrate away from in-memory store
- [x] Auth — user accounts (Supabase Auth); jobs scoped to user (`auth`)

## Phase 4 — Deploy & Polish

- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway or Render (requires PostgreSQL + Redis add-ons)
- [ ] Export speed — download all 4 stems from Supabase in parallel before mixing (currently sequential; easy win)
- [ ] Separation progress bar — stream Demucs progress to the frontend via SSE; worker publishes progress to Redis, API streams to client
- [ ] UX polish — upload progress indicator, waveform loading states, error surfaces, mobile layout
- [x] Performance — MP3 stem storage (~10× faster waveform load), DEMUCS_DEVICE env var for GPU, processing_ms timing (`performance`)

## Phase 5 — Audio Intelligence

- [ ] 6-stem separation — switch Demucs model from `htdemucs` to `htdemucs_6s`; adds dedicated `guitar` and `piano` stems, shrinks `other` to remaining instruments (synths, brass, strings, etc.)
- [ ] Instrument detection — classify instruments present in the `other` stem (label the unknown content)
- [ ] Pitch/chord extraction — run pitch detection (e.g. `crepe`) on single-instrument stems to surface notes and chords
