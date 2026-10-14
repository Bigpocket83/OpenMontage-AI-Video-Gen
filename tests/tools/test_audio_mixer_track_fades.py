"""Regression tests for delayed per-track fades in ``audio_mixer``."""

import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.audio.audio_mixer import AudioMixer  # noqa: E402


@pytest.mark.parametrize("operation", ["mix", "full_mix"])
def test_delayed_track_fades_use_the_source_timeline(tmp_path, monkeypatch, operation):
    """Fade source audio before delay, and start fade-out at its real end."""
    tone = tmp_path / "tone.wav"
    tone.write_bytes(b"stub")
    commands = []

    def fake_run(self, cmd, **kwargs):
        commands.append(list(cmd))
        if cmd[0] == "ffprobe":
            return SimpleNamespace(stdout="2.0\n", stderr="")
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(AudioMixer, "run_command", fake_run)
    result = AudioMixer().execute(
        {
            "operation": operation,
            "tracks": [{
                "path": str(tone),
                "role": "speech",
                "start_seconds": 1,
                "fade_in_seconds": 0.25,
                "fade_out_seconds": 0.5,
            }],
            "ducking": {"enabled": False},
            "normalize": False,
            "output_path": str(tmp_path / "out.wav"),
        }
    )

    assert result.success, result.error
    ffmpeg_cmd = next(cmd for cmd in commands if cmd[0] == "ffmpeg")
    filter_graph = ffmpeg_cmd[ffmpeg_cmd.index("-filter_complex") + 1]
    assert (
        "afade=t=in:d=0.25,afade=t=out:st=1.5:d=0.5,adelay=1000|1000"
        in filter_graph
    )


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_delayed_track_with_fade_out_remains_audible_after_its_start(tmp_path):
    """End-to-end regression for #347: delayed audio must not be silenced."""
    tone = tmp_path / "tone.wav"
    output = tmp_path / "mixed.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", str(tone)],
        capture_output=True,
        check=True,
        timeout=30,
    )

    result = AudioMixer().execute(
        {
            "operation": "mix",
            "tracks": [{
                "path": str(tone),
                "role": "music",
                "start_seconds": 1,
                "fade_out_seconds": 0.5,
            }],
            "normalize": False,
            "output_path": str(output),
        }
    )
    assert result.success, result.error

    measured = subprocess.run(
        [
            "ffmpeg", "-ss", "1.25", "-t", "0.25", "-i", str(output),
            "-vn", "-af", "volumedetect", "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    mean_line = next(line for line in measured.stderr.splitlines() if "mean_volume" in line)
    mean_db = float(mean_line.split("mean_volume:")[1].strip().split(" ")[0])
    assert mean_db > -60, f"delayed tone was unexpectedly silent: {mean_db} dB"


@pytest.mark.parametrize("probe_output", ["N/A\n", "", "0.0\n", "nan\n"])
def test_fade_out_on_track_with_unknown_duration_names_the_track(
    tmp_path, monkeypatch, probe_output
):
    """#771: an unusable ffprobe duration must not surface as a raw float() error."""
    track = tmp_path / "empty.wav"
    track.write_bytes(b"stub")

    def fake_run(self, cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return SimpleNamespace(stdout=probe_output, stderr="")
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(AudioMixer, "run_command", fake_run)
    result = AudioMixer().execute(
        {
            "operation": "full_mix",
            "tracks": [{"path": str(track), "role": "speech", "fade_out_seconds": 0.2}],
            "normalize": False,
            "target_duration": 1,
            "output_path": str(tmp_path / "mixed.wav"),
        }
    )

    assert not result.success
    assert "could not convert" not in result.error
    assert str(track) in result.error
    assert "duration" in result.error


@pytest.mark.skipif(shutil.which("ffprobe") is None, reason="ffprobe required")
def test_zero_sample_wav_with_fade_out_is_rejected_with_a_clear_error(tmp_path):
    """End-to-end #771: ffprobe reports N/A for a zero-sample WAV."""
    import wave

    track = tmp_path / "empty.wav"
    with wave.open(str(track), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(22050)
        audio.writeframes(b"")

    result = AudioMixer().execute(
        {
            "operation": "full_mix",
            "tracks": [{"path": str(track), "role": "speech", "fade_out_seconds": 0.2}],
            "normalize": False,
            "target_duration": 1,
            "output_path": str(tmp_path / "mixed.wav"),
        }
    )

    assert not result.success
    assert "Cannot determine the duration of track" in result.error
    assert str(track) in result.error
