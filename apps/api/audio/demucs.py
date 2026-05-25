import os
from pathlib import Path


STEM_NAMES = ("vocals", "drums", "bass", "other")


def get_demucs_device() -> str:
    if "DEMUCS_DEVICE" in os.environ:
        return os.environ["DEMUCS_DEVICE"]
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def separate(input_path: str, output_dir: str, device: str | None = None) -> dict[str, str]:
    from demucs.separate import main as demucs_main

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    demucs_main(
        [
            "--name", "htdemucs",
            "--device", device or get_demucs_device(),
            "--out", str(out),
            "--filename", "{stem}.{ext}",
            str(input_path),
        ]
    )

    stems: dict[str, str] = {}
    for stem_name in STEM_NAMES:
        matches = list(out.rglob(f"{stem_name}.wav"))
        if matches:
            stems[stem_name] = str(matches[0])

    missing = [s for s in STEM_NAMES if s not in stems]
    if missing:
        raise RuntimeError(f"Demucs did not produce stems: {missing}")

    return stems
