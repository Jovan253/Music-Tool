## Context

Demucs writes 4 uncompressed WAV stems (~40 MB each at 44.1 kHz stereo for a 4-minute song). These are uploaded to Supabase and served via signed URL. WaveSurfer fetches the full file before it can render a waveform — so the user stares at a spinner while ~160 MB downloads. Converting to MP3 at 256 kbps cuts each stem to ~4 MB (~16 MB total), making waveform load ~10× faster with no code changes on the frontend side.

The export path (mixer.py) already uses pydub, which reads both WAV and MP3 via ffmpeg — so the change there is one argument string.

## Goals / Non-Goals

**Goals:**
- Store stems as MP3 (256 kbps) in Supabase — faster download, faster waveform render
- `DEMUCS_DEVICE` env var for explicit GPU/CPU control on deployment
- `processing_ms` on job record for observability

**Non-Goals:**
- Serving a separate low-bitrate preview vs. high-quality export (added complexity, not needed)
- Per-request model selection
- Lossless export from MP3 stems (export quality from MP3 source is fine for a practice tool)

## Decisions

### Store MP3, not dual WAV+MP3

Simplest path: Demucs writes WAV → transcode each stem to MP3 in the worker → upload MP3 → delete local WAV. No extra Supabase paths, no schema changes beyond the file extension in the stored path.

Alternative considered: keep WAV for export quality, serve MP3 only for preview. Rejected — adds two storage paths per stem, complicates the export route, and 256 kbps MP3 is transparent quality for a practice tool.

### pydub for transcoding

pydub is already installed (used in mixer.py). `AudioSegment.from_wav(path).export(mp3_path, format="mp3", bitrate="256k")` is one call, and ffmpeg is already a system dependency. No new packages.

### mixer.py format arg

Change `AudioSegment.from_file(..., format="wav")` → `format="mp3"`. pydub handles both via ffmpeg; no other changes needed.

### DEMUCS_DEVICE default — auto-detect at call time

`torch.cuda.is_available()` checked when the worker runs (not at import time), so a CPU-only dev machine and a GPU prod machine can share the same code with no env config needed locally.

### processing_ms — nullable integer column

`INTEGER NULL` — no sentinel value, clean null for failed/pre-migration rows.

## Risks / Trade-offs

- [Transcoding time] MP3 encoding adds ~5-15s per stem on CPU. This runs after Demucs (which takes minutes), so it's noise in the total job time. → Acceptable.
- [Export quality] MP3→MP3 re-encode or MP3→WAV upsample slightly degrades quality vs. WAV source. → Acceptable for a practice tool; can be revisited if lossless export becomes a requirement.
- [First-run model download] Demucs downloads ~300 MB of model weights on first use. `processing_ms` will be inflated on cold start. → Document in `.env.example`.
- [CUDA env var mismatch] If `DEMUCS_DEVICE=cuda` is set but no GPU is present, Demucs raises and the worker marks the job `failed`. → Expected behaviour; the error message is clear.

## Migration Plan

1. Add Alembic migration for `processing_ms` column
2. Update worker: transcode WAV → MP3 after separation, write `processing_ms`
3. Update mixer.py to read MP3
4. Deploy — new jobs store MP3; existing done jobs in Supabase still have WAV paths (those jobs won't be re-processed, which is fine)
5. Rollback: revert worker and mixer, redeploy — existing MP3 jobs would fail to export (stems are MP3 but mixer expects WAV). If rollback is needed, also clear affected jobs from DB.
