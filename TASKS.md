# Music Tool — Project Tasks

High-level roadmap. Each item links to its OpenSpec change or notes the current status.
Detailed per-change tasks live in `openspec/changes/<name>/tasks.md`.

---

## Phase 1 — Local Prototype

- [x] Monorepo setup — React + TypeScript frontend, FastAPI backend, shared env config (`monorepo-setup`)
- [x] Audio upload — drag-and-drop UI, `POST /upload`, in-memory job store, `GET /jobs/{job_id}` (`audio-upload`)
- [ ] Demucs worker — stem separation wired to upload, job status polling (`demucs-worker`) ← in progress

## Phase 2 — Basic Web App

- [ ] Stem mixer — multi-track waveform playback (WaveSurfer.js), mute/solo/volume per stem
- [ ] Export — render and download a custom mix as mp3 or wav

## Phase 3 — Production Infrastructure

- [ ] Async job queue — replace daemon thread with Redis + Celery (or RQ); add job progress events
- [ ] Cloud storage — move uploads and stems to Supabase Storage or S3; presigned URLs for playback
- [ ] Database — PostgreSQL job/user records via SQLAlchemy; migrate away from in-memory store
- [ ] Auth — user accounts (Supabase Auth or Auth.js); jobs scoped to user

## Phase 4 — Deploy & Polish

- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway or Render
- [ ] Performance — GPU inference path, htdemucs_ft model option, processing time targets
- [ ] UX polish — upload progress, waveform loading states, error surfaces, mobile layout
