import io
import shutil
import tempfile
from pathlib import Path

import modal

app = modal.App("music-tool-separation")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.5.1",
        "torchaudio==2.5.1",
        "demucs>=4.0",
        "pydub>=0.25",
    )
    .apt_install("ffmpeg")
)

_STEM_NAMES = ("vocals", "drums", "bass", "other")


@app.function(gpu="T4", image=image, timeout=300)
def separate_on_gpu(audio_bytes: bytes) -> dict[str, bytes]:
    from demucs.separate import main as demucs_main
    from pydub import AudioSegment

    tmp_dir = tempfile.mkdtemp()
    try:
        input_file = Path(tmp_dir) / "input.audio"
        input_file.write_bytes(audio_bytes)

        out_dir = Path(tmp_dir) / "stems"
        out_dir.mkdir(parents=True, exist_ok=True)

        demucs_main([
            "--name", "htdemucs",
            "--device", "cuda",
            "--out", str(out_dir),
            "--filename", "{stem}.{ext}",
            str(input_file),
        ])

        result: dict[str, bytes] = {}
        for stem_name in _STEM_NAMES:
            matches = list(out_dir.rglob(f"{stem_name}.wav"))
            if not matches:
                continue
            buf = io.BytesIO()
            AudioSegment.from_wav(str(matches[0])).export(buf, format="mp3", bitrate="256k")
            result[stem_name] = buf.getvalue()

        missing = [s for s in _STEM_NAMES if s not in result]
        if missing:
            raise RuntimeError(f"Demucs did not produce stems: {missing}")

        return result
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
