## ADDED Requirements

### Requirement: Modal app defines a GPU-backed separation function
`apps/api/audio/modal_separation.py` SHALL define a Modal app with an image that includes PyTorch 2.5.1, torchaudio 2.5.1, Demucs, pydub, and FFmpeg. The app SHALL expose a function `separate_on_gpu` decorated with `@app.function(gpu="T4")` that accepts raw audio bytes and a stem name list, runs `htdemucs`, transcodes each WAV stem to MP3 at 256 kbps, and returns a dict of `{stem_name: mp3_bytes}`.

#### Scenario: GPU function returns MP3 bytes for all stems
- **WHEN** `separate_on_gpu.remote(audio_bytes)` is called with valid audio bytes
- **THEN** the function returns a dict with keys `vocals`, `drums`, `bass`, `other`, each mapping to non-empty MP3 bytes

#### Scenario: Modal image has required packages
- **WHEN** the Modal container starts
- **THEN** `import demucs`, `import torch`, and `from pydub import AudioSegment` all succeed without errors

### Requirement: Modal credentials are configured via environment variables
The system SHALL read `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` from environment variables to authenticate with Modal. These SHALL be documented in `.env.example`.

#### Scenario: Worker authenticates with Modal
- **WHEN** `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` are set in the environment
- **THEN** calling `separate_on_gpu.remote(...)` succeeds without authentication errors

### Requirement: Modal function is deployed before worker starts
The Modal app SHALL be deployed once via `modal deploy` before the Railway worker is started. The deployed function name SHALL be stable across deploys so the worker can call it by reference.

#### Scenario: Deployed function is callable
- **WHEN** the Modal app has been deployed and the worker calls `separate_on_gpu.remote(...)`
- **THEN** the call succeeds and returns stem bytes without requiring a local Modal process
