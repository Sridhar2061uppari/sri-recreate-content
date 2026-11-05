"""
Integration test: verifies that the 9.7x compression problem is fixed.

Before fix: 29 scenes -> 3 beats (9.7x compression)
After fix : 29 scenes -> 8+ beats for 8s (<=3.6x compression)
No API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import beats_for_duration, _plan_prompt


class TestCompressionRatios:

    def test_chicken_29_scenes_compression_below_4x(self):
        """The chicken video (29 scenes) must compress by less than 4x."""
        scene_count = 29
        beats = beats_for_duration(8, scene_count)
        compression = scene_count / beats
        assert compression < 4.0, (
            f"Compression ratio {compression:.1f}x is still too high "
            f"(scenes={scene_count}, beats={beats}). Max allowed: 4.0x"
        )

    def test_cats_10_scenes_compression_reasonable(self):
        scene_count = 10
        beats = beats_for_duration(8, scene_count)
        compression = scene_count / beats
        assert compression <= 3.0, (
            f"Cats compression {compression:.1f}x exceeds 3.0x limit"
        )

    def test_yt_1_scene_no_over_beat(self):
        """A 1-scene video must not get padded with unnecessary beats."""
        beats = beats_for_duration(8, 1)
        assert beats <= 3

    def test_old_formula_was_3_beats(self):
        """Confirm original formula gave 3 beats for 8s (regression marker)."""
        old_result = max(2, min(6, round(8 * 0.375)))
        assert old_result == 3

    def test_new_formula_exceeds_old_for_dense_videos(self):
        old = max(2, min(6, round(8 * 0.375)))
        new = beats_for_duration(8, 29)
        assert new > old, f"New formula ({new}) should exceed old ({old}) for 29-scene video"

    def test_10s_video_with_29_scenes(self):
        beats = beats_for_duration(10, 29)
        compression = 29 / beats
        assert compression < 4.0


class TestPlanPromptContainsSceneList:
    """The plan prompt must include the full scene list."""

    def test_chicken_scene_list_length(self, chicken_analysis, chicken_media):
        n = len(chicken_analysis.scenes)
        beat_count = beats_for_duration(8, n)
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, beat_count)
        for i in range(1, n + 1):
            assert f"S{i} [" in prompt, f"Missing S{i} from prompt scene list"

    def test_beat_count_matches_scene_density(self, chicken_analysis):
        n = len(chicken_analysis.scenes)
        beats = beats_for_duration(8, n)
        assert beats > 3, f"Expected >3 beats for {n} scenes, got {beats}"
