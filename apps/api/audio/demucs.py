from pathlib import Path


STEM_NAMES = ("vocals", "drums", "bass", "other")


def separate(input_path: str, output_dir: str) -> dict[str, str]:
    """Run htdemucs on input_path, write stems to output_dir, return stem name → file path."""
    from demucs.separate import main as demucs_main

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    demucs_main(
        [
            "--name", "htdemucs",
            "--out", str(out),
            "--filename", "{stem}.{ext}",
            str(input_path),
        ]
    )

    # Demucs writes to <out>/htdemucs/<track_name>/{stem}.wav
    # With --filename {stem}.{ext} it writes directly to <out>/htdemucs/<track_stem>
    # Find the stems by searching the output tree
    stems: dict[str, str] = {}
    for stem_name in STEM_NAMES:
        matches = list(out.rglob(f"{stem_name}.wav"))
        if matches:
            stems[stem_name] = str(matches[0])

    missing = [s for s in STEM_NAMES if s not in stems]
    if missing:
        raise RuntimeError(f"Demucs did not produce stems: {missing}")

    return stems
