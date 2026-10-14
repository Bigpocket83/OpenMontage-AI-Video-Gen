"""Scheduling delays apply to every source channel, including surround audio."""

import shutil
import struct
import wave

import pytest

from tools.audio.audio_mixer import AudioMixer

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg required")


@pytest.mark.parametrize("operation", ["mix", "full_mix"])
@pytest.mark.parametrize("channels,delay", [(1, 1), (2, 1), (6, 1), (6, 0)])
def test_scheduled_track_keeps_channels_on_the_same_timeline(tmp_path, operation, channels, delay):
    source, output = tmp_path / "source.wav", tmp_path / "mixed.wav"
    rate = 16000
    amplitudes = tuple(1000 * (channel + 1) for channel in range(channels))
    with wave.open(str(source), "wb") as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(struct.pack("<" + "h" * channels, *amplitudes) * rate)
    result = AudioMixer().execute({
        "operation": operation, "output_path": str(output), "normalize": False,
        "tracks": [{"path": str(source), "role": "sfx", "start_seconds": delay}],
    })
    assert result.success, result.error
    with wave.open(str(output), "rb") as audio:
        assert audio.getnchannels() == channels
        assert audio.getframerate() == rate
        count = audio.getnframes()
        samples = struct.unpack("<" + "h" * (count * channels), audio.readframes(count))
    # Oracle from the declared schedule and input PCM, not from a filter string:
    # each channel is silent before the scheduled onset and carries its own
    # source amplitude after onset. Mono/stereo/no-delay controls remain valid.
    if delay:
        early = samples[int(.1 * rate) * channels:int(.2 * rate) * channels]
        assert all(value == 0 for value in early)
    for channel, amplitude in enumerate(amplitudes):
        start, end = int((delay + .1) * rate), int((delay + .2) * rate)
        active = samples[start * channels + channel:end * channels:channels]
        assert active
        assert max(abs(value - amplitude) for value in active) <= 1
