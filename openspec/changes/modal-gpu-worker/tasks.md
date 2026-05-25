## 1. Dependencies and credentials

- [x] 1.1 Add `modal>=0.64` to `apps/api/pyproject.toml` dependencies
- [x] 1.2 Add `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` to `apps/api/.env.example` with comments
- [x] 1.3 Create a Modal account at modal.com and generate a token (Settings → API Tokens) — store in local `.env`

## 2. Modal function

- [x] 2.1 Create `apps/api/audio/modal_separation.py` — define Modal app with image (torch==2.5.1, torchaudio==2.5.1, demucs, pydub, ffmpeg) and a `@app.function(gpu="T4")` function `separate_on_gpu(audio_bytes: bytes) -> dict[str, bytes]` that writes audio to a temp file, runs `htdemucs`, transcodes each WAV stem to MP3 at 256k, and returns `{stem_name: mp3_bytes}`
- [x] 2.2 Deploy the Modal app once: `cd apps/api && modal deploy audio/modal_separation.py`

## 3. Worker integration

- [x] 3.1 Update `apps/api/workers/separation.py` — if `MODAL_TOKEN_ID` is set, call `separate_on_gpu.remote(audio_bytes)` to get `{stem_name: mp3_bytes}` dict, then upload each to Supabase; otherwise fall back to existing local `separate()` path
- [x] 3.2 Update `apps/api/routes/upload.py` — reduce `job_timeout` back to 120s

## 4. Railway config

- [x] 4.1 Add `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` to Railway worker service environment variables
- [x] 4.2 Push to main and verify Railway worker redeploys cleanly

## 5. Smoke test

- [x] 5.1 Upload a short clip via the deployed frontend — confirm job completes in under 60 seconds and all 4 stems load
