import io
import math
from pydub import AudioSegment

STEM_NAMES = ("vocals", "drums", "bass", "other")


def mix_stems(stems: dict[str, bytes], volumes: dict[str, float], fmt: str) -> bytes:
    """Overlay stems with per-stem gain, return encoded audio bytes."""
    mixed: AudioSegment | None = None
    first_data: bytes | None = None

    for name in STEM_NAMES:
        data = stems.get(name)
        if not data:
            continue
        if first_data is None:
            first_data = data
        vol = volumes.get(name, 1.0)
        segment = AudioSegment.from_file(io.BytesIO(data), format="mp3")
        if vol <= 0:
            continue
        if vol < 1.0:
            gain_db = 20 * math.log10(vol)
            segment = segment + gain_db
        mixed = segment if mixed is None else mixed.overlay(segment)

    if mixed is None:
        # all stems muted — return silence matching first stem duration
        duration = len(AudioSegment.from_file(io.BytesIO(first_data), format="mp3")) if first_data else 0
        mixed = AudioSegment.silent(duration=duration)

    buf = io.BytesIO()
    mixed.export(buf, format=fmt)
    return buf.getvalue()
