## Context

Demucs separation on Railway CPU takes ~12 minutes for a 2-minute song — effectively unusable. Modal provides serverless GPU containers billed per second of compute. The existing RQ-based worker architecture stays intact; only the separation step is offloaded to Modal. The Railway worker becomes a lightweight dispatcher.

## Goals / Non-Goals

**Goals:**
- `apps/api/audio/modal_separation.py` defines a Modal app with a GPU-backed function that accepts audio bytes, runs `htdemucs`, transcodes to MP3, and returns a dict of `{stem_name: mp3_bytes}`
- `workers/separation.py` calls the Modal function instead of the local `separate()` function
- Railway worker no longer installs PyTorch/Demucs (lighter builds, faster deploys)
- RQ job timeout reduced back to 120s
- `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` documented in `.env.example`

**Non-Goals:**
- Removing RQ/Redis (queue stays for job lifecycle management)
- Streaming progress from Modal back to the frontend (separate future change)
- Supporting GPUs other than T4 (sufficient for htdemucs)
- Running Modal locally in dev (local separation via `DEMUCS_DEVICE` stays as fallback)

## Decisions

**Modal function returns MP3 bytes rather than uploading to Supabase directly**
Keeps Supabase credentials out of Modal's environment. The Railway worker already has Supabase access and handles the upload. Modal's job is purely compute: bytes in, bytes out. Simpler secret management.

**Modal image pins `torch==2.5.1` to match local dev**
Avoids surprises from torchaudio version drift (torchaudio 2.11 dropped soundfile on Windows; the pin protects parity). Modal's image builder caches layers so this only costs time on first deploy.

**Local separation kept as dev fallback**
`workers/separation.py` checks for `MODAL_TOKEN_ID` in the environment. If absent (local dev without Modal credentials), it falls back to the existing local `separate()` call. No dev workflow disruption.

**T4 GPU for cost/performance balance**
An NVIDIA T4 on Modal costs ~$0.00022/second. A 2-minute song takes ~25s of GPU time ≈ $0.006 per job. An A10G would be ~2× faster but ~3× the cost — T4 is sufficient for htdemucs.

## Risks / Trade-offs

- **Modal cold start (~15–30s on first job)** → Acceptable for MVP; subsequent jobs reuse warm containers. Can be mitigated later with `modal.keep_warm(1)` if budget allows.
- **Modal outage** → Fallback: set `DEMUCS_DEVICE=cpu` on the worker and jobs process slowly but correctly. No data loss.
- **MP3 bytes transferred over network (worker → Modal → worker)** → A 2-min audio file is ~3MB in, ~4×1MB MP3 stems out. Negligible at Modal's internal network speeds.
- **Railway worker build is now lighter** → No torch/demucs means faster builds. Potential issue: if someone accidentally runs the worker without `MODAL_TOKEN_ID`, it falls back to CPU (safe, slow, logged).

## Migration Plan

1. Create Modal account, generate token
2. Add `modal` to `pyproject.toml`
3. Write `apps/api/audio/modal_separation.py`
4. Update `workers/separation.py` to call Modal when credentials present
5. Set `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` on Railway worker service
6. Deploy Modal app once: `modal deploy apps/api/audio/modal_separation.py`
7. Push to main → Railway redeploys worker
8. Smoke test: upload a short clip, verify separation completes in <60s
9. Rollback: unset `MODAL_TOKEN_ID` on Railway worker → falls back to CPU separation
