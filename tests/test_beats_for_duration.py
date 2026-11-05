"""
Tests for beats_for_duration() – the dynamic beat-count function.

All tests are pure logic; no API calls, no file I/O.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import beats_for_duration


class TestBeatsForDurationOriginalFormula:
    """Without scene_count the old 0.375 b/s formula must still hold."""

    def test_8s_no_scenes_returns_3(self):
        assert beats_for_duration(8) == 3

    def test_10s_no_scenes_returns_4(self):
        assert beats_for_duration(10) == 4

    def test_zero_scene_count_same_as_no_arg(self):
        for s in (8, 10):
            assert beats_for_duration(s, 0) == beats_for_duration(s)

    def test_minimum_always_2(self):
        assert beats_for_duration(1) == 2
        assert beats_for_duration(2) == 2


class TestBeatsForDurationSceneDensity:
    """With scene_count, beat count should scale up for dense videos."""

    def test_high_scene_count_increases_beats(self):
        # 29 scenes (chicken video) -> should be > 3 for 8s
        beats_with = beats_for_duration(8, scene_count=29)
        beats_without = beats_for_duration(8)
        assert beats_with > beats_without, (
            f"Expected more beats with 29 scenes ({beats_with}) than without ({beats_without})"
        )

    def test_10_scenes_cats_video(self):
        beats = beats_for_duration(8, scene_count=10)
        assert beats >= 3, "10-scene video should get at least 3 beats for 8s"

    def test_1_scene_yt_video_not_excessive(self):
        beats = beats_for_duration(8, scene_count=1)
        assert beats <= 3, "1-scene video should not get more than 3 beats"

    def test_never_exceeds_duration_seconds(self):
        """Hard cap: beats <= duration so every beat is >= 1s."""
        for duration in (8, 10):
            for sc in (1, 5, 10, 29, 50):
                assert beats_for_duration(duration, sc) <= duration, (
                    f"beats_for_duration({duration}, {sc}) exceeds duration"
                )

    def test_always_at_least_base(self):
        """Scene-density path must never go below the base formula."""
        for duration in (8, 10):
            base = beats_for_duration(duration)
            for sc in range(1, 30):
                assert beats_for_duration(duration, sc) >= base

    def test_29_scenes_8s_gets_more_beats_than_3(self):
        """Regression: chicken video was getting only 3 beats, must get more."""
        assert beats_for_duration(8, 29) > 3

    def test_29_scenes_10s_reasonable_cap(self):
        result = beats_for_duration(10, 29)
        assert 4 <= result <= 10

    @pytest.mark.parametrize("sc,expected_min", [
        (3, 2),
        (6, 2),
        (9, 3),
        (12, 4),
        (29, 4),
    ])
    def test_scene_density_parametric(self, sc, expected_min):
        result = beats_for_duration(8, sc)
        assert result >= expected_min, f"sc={sc} expected >= {expected_min}, got {result}"
