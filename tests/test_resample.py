"""
Tests for _resample_for_gemini() – the 2fps pre-processing step.

Uses the real downloaded video files from work/downloads/.
No API calls.
"""
import sys, subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from recreate_video import _resample_for_gemini, ffmpeg_exe, _noop_notify

DOWNLOADS = PROJECT_ROOT / "work" / "downloads"
SHA_CHICKEN = "e0710bb8682339cb372613ecf57f85ae81822f0c718b62f1c829626d94cfac7c"


@pytest.fixture(scope="module")
def chicken_video():
    path = DOWNLOADS / (SHA_CHICKEN + ".mp4")
    if not path.exists():
        pytest.skip("Chicken video not downloaded – skipping resample tests.")
    return path


@pytest.fixture(autouse=True)
def cleanup_2fps(chicken_video):
    """Remove any _2fps.mp4 temp file before and after each test."""
    out = chicken_video.with_name(chicken_video.stem + "_2fps.mp4")
    if out.exists():
        out.unlink()
    yield
    if out.exists():
        out.unlink()


class TestResampleOutput:

    def test_returns_path_object(self, chicken_video):
        result = _resample_for_gemini(chicken_video, _noop_notify)
        assert isinstance(result, Path)

    def test_2fps_file_created(self, chicken_video):
        out = chicken_video.with_name(chicken_video.stem + "_2fps.mp4")
        _resample_for_gemini(chicken_video, _noop_notify)
        assert out.exists(), "2fps temp file was not created"

    def test_output_file_is_smaller_than_original(self, chicken_video):
        out = chicken_video.with_name(chicken_video.stem + "_2fps.mp4")
        _resample_for_gemini(chicken_video, _noop_notify)
        assert out.stat().st_size < chicken_video.stat().st_size, (
            "2fps file should be smaller than original 30fps file"
        )

    def test_output_is_valid_mp4(self, chicken_video):
        out = chicken_video.with_name(chicken_video.stem + "_2fps.mp4")
        _resample_for_gemini(chicken_video, _noop_notify)
        result = subprocess.run(
            [ffmpeg_exe(), "-v", "error", "-i", str(out), "-f", "null", "-"],
            capture_output=True,
        )
        assert result.returncode == 0, f"ffmpeg says 2fps file is corrupt: {result.stderr.decode()[:300]}"

    def test_idempotent_when_file_exists(self, chicken_video):
        """Calling twice returns existing file without re-encoding."""
        out = chicken_video.with_name(chicken_video.stem + "_2fps.mp4")
        r1 = _resample_for_gemini(chicken_video, _noop_notify)
        mtime1 = out.stat().st_mtime
        r2 = _resample_for_gemini(chicken_video, _noop_notify)
        mtime2 = out.stat().st_mtime
        assert r1 == r2
        assert mtime1 == mtime2, "File was re-encoded even though it already existed"

    def test_fallback_to_original_on_bad_path(self, tmp_path):
        """If ffmpeg fails (bad input), function returns original path unchanged."""
        fake = tmp_path / "nonexistent.mp4"
        fake.touch()  # empty file – ffmpeg will fail on it
        result = _resample_for_gemini(fake, _noop_notify)
        assert result == fake, "Should fall back to original path on ffmpeg failure"
