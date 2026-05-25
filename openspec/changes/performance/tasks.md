## 1. Demucs wrapper — device config

- [x] 1.1 Update `apps/api/audio/demucs.py` to accept a `device` parameter; pass it as `--device` to `demucs_main`; add `get_demucs_device()` helper that reads `DEMUCS_DEVICE` env var, defaulting to `"cuda"` if `torch.cuda.is_available()` else `"cpu"`
- [x] 1.2 Add commented `DEMUCS_DEVICE` entry to `apps/api/.env.example` explaining auto-detect default and valid values

## 2. MP3 transcoding in worker

- [x] 2.1 After `separate()` returns WAV paths, transcode each stem WAV → MP3 at 256 kbps using pydub (`AudioSegment.from_wav(path).export(mp3_path, format="mp3", bitrate="256k")`)
- [x] 2.2 Upload the MP3 files to Supabase (replace the WAV upload calls); delete local WAV and MP3 temp files after upload
- [x] 2.3 Update `apps/api/audio/mixer.py`: change `format="wav"` → `format="mp3"` in `AudioSegment.from_file()` calls

## 3. Database — processing_ms column

- [x] 3.1 Add `processing_ms = Column(Integer, nullable=True)` to the `Job` SQLAlchemy model
- [x] 3.2 Generate Alembic migration (`alembic revision --autogenerate -m "add processing_ms to jobs"`) and verify the generated file looks correct
- [x] 3.3 Run `alembic upgrade head` and confirm the column exists
- [x] 3.4 Add `processing_ms: int | None` to the `JobResponse` Pydantic schema

## 4. Worker — timing + wiring

- [x] 4.1 Wrap the `separate()` call with `time.monotonic()` to measure wall-clock ms; pass `device=get_demucs_device()` to `separate()`
- [x] 4.2 Write `processing_ms` to the job record on successful completion

## 5. Frontend — display processing time

- [x] 5.1 Add `processing_ms: number | null` to the `JobResponse` TypeScript type in `apps/web/src/lib/api.ts`
- [x] 5.2 In `StemMixer.tsx`, fetch the job record on mount (reuse `getJobStatus`) and display "Separated in Xs" in the header when `processing_ms` is non-null
