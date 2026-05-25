## Why

Demucs separation on Railway CPU takes ~12 minutes for a 2-minute song, making the app unusable. Offloading inference to a Modal T4 GPU reduces that to ~20–30 seconds with no idle cost — Modal charges only while a job is running.

## What Changes

- Add `apps/api/audio/modal_separation.py` — a Modal app defining a GPU-backed separation function with PyTorch + Demucs installed in its image
- Modify `apps/api/workers/separation.py` — instead of running Demucs locally, call the Modal function and await the result; upload stems and update job status as before
- Add `modal` to `pyproject.toml` dependencies
- Add `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` env vars to Railway worker service and `.env.example`
- Drop RQ `job_timeout` back to 120s (GPU separation is fast)
- Railway worker service no longer needs PyTorch/Demucs/FFmpeg — build becomes significantly lighter

## Capabilities

### New Capabilities

- `modal-gpu-separation`: Modal function definition, image spec (PyTorch + Demucs + FFmpeg), GPU class selection, and the separation entrypoint that accepts audio bytes and returns stem MP3 bytes

### Modified Capabilities

- `stem-separation`: Separation is no longer performed locally — it is dispatched to Modal GPU infrastructure. The requirement that separation completes within a reasonable time is now met via GPU rather than CPU.

## Impact

- `apps/api/audio/modal_separation.py` — new file
- `apps/api/workers/separation.py` — replace local `separate()` call with Modal call
- `apps/api/pyproject.toml` — add `modal` dependency
- `apps/api/.env.example` — add Modal token vars
- Railway worker service: remove PyTorch/Demucs from build (lighter); add Modal token env vars
- No frontend changes
- No database or storage changes
