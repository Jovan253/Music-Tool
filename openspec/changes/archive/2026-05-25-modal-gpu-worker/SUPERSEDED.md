This change was implemented in May 2026. It still stands in spirit — separation
runs on a Modal T4 — but `modal-api-host` (2026-09-26) reshaped it, so the
details below are out of date.

What changed:

- The GPU function no longer takes audio bytes and returns stem bytes. It takes a
  `job_id` and owns the whole job: download, separate, transcode, upload, and the
  terminal status write.
- It moved from `apps/api/audio/modal_separation.py` to
  `apps/api/modal_separation.py`, and is named `separate_job`, not
  `separate_on_gpu`.
- This change deliberately kept Supabase credentials out of Modal so the function
  stayed "purely compute: bytes in, bytes out". That reasoning depended on a
  trusted RQ worker existing to do the storage I/O. `modal-api-host` deleted the
  worker, so the credentials moved into a Modal secret instead.
- The `modal-gpu-separation` capability was never promoted into
  `openspec/specs/`; its requirements now live in
  `openspec/specs/modal-api-host/spec.md`.

Current behaviour is specified in `openspec/specs/modal-api-host/spec.md` and
`openspec/specs/stem-separation/spec.md`.
