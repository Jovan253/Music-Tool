import io
import math
from pydub import AudioSegment

STEM_NAMES = ("vocals", "drums", "bass", "other")


def mix_stems(stems: dict[str, str], volumes: dict[str, float], fmt: str) -> bytes:
    """Overlay stems with per-stem gain, return encoded audio bytes."""
    mixed: AudioSegment | None = None

    for name in STEM_NAMES:
        path = stems.get(name)
        if not path:
            continue
        vol = volumes.get(name, 1.0)
        segment = AudioSegment.from_wav(path)
        if vol <= 0:
            # fully muted — skip this stem
            continue
        if vol < 1.0:
            gain_db = 20 * math.log10(vol)
            segment = segment + gain_db
        mixed = segment if mixed is None else mixed.overlay(segment)

    if mixed is None:
        # all stems muted — return silence matching first stem duration
        first_path = next(iter(stems.values()))
        mixed = AudioSegment.silent(duration=len(AudioSegment.from_wav(first_path)))

    buf = io.BytesIO()
    mixed.export(buf, format=fmt)
    return buf.getvalue()
