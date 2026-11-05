"""
Tests for _plan_prompt() – the Gemini instruction text.

Checks that every new section and rule is present in the generated text.
No API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import _plan_prompt, beats_for_duration
from tests.conftest import make_mock_plan


class TestPlanPromptHookSection:
    """Beat 1 must be a mandatory HOOK with social media rules."""

    def test_hook_section_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "HOOK-FIRST STRUCTURE" in prompt

    def test_hook_label_mandatory_instruction(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "Beat 1 label MUST be" in prompt
        assert "HOOK" in prompt

    def test_audio_muted_instruction(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "AUDIO MUTED" in prompt

    def test_payoff_first_instruction(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "payoff" in prompt.lower() or "result" in prompt.lower()

    def test_hook_uses_analysis_hook_text(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        # The analysis hook text should appear inside the prompt
        hook_fragment = chicken_analysis.hook[:30]
        assert hook_fragment in prompt


class TestPlanPromptSceneList:
    """Scene list must appear so Gemini groups real cuts."""

    def test_scene_list_header_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "SOURCE SCENE LIST" in prompt

    def test_all_scenes_listed(self, chicken_analysis, chicken_media):
        n = len(chicken_analysis.scenes)
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        # Each scene is listed as S1, S2, ... Sn
        for i in range(1, n + 1):
            assert f"S{i} [" in prompt, f"Scene S{i} missing from scene list"

    def test_cats_scenes_listed(self, cats_analysis, cats_media):
        n = len(cats_analysis.scenes)
        prompt = _plan_prompt(cats_analysis, cats_media, 8, beats_for_duration(8, n))
        assert f"S{n} [" in prompt


class TestPlanPromptCameraRules:
    """Camera-precision rules must be present to suppress zoom bias."""

    def test_camera_rules_section(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "CAMERA RULES" in prompt

    def test_locked_off_instruction(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "locked-off" in prompt.lower()

    def test_no_zoom_no_pan_instruction(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "no zoom" in prompt.lower()


class TestPlanPromptAudioRules:
    """Audio timestamp rules must be in the prompt."""

    def test_audio_section_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "AUDIO RULES" in prompt

    def test_timestamp_example_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "0.0s:" in prompt


class TestPlanPromptGlobalAvoids:
    """Global avoid items must be embedded in the plan prompt."""

    def test_global_avoid_section(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "AVOID" in prompt

    def test_zoom_global_avoid_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "Unprompted camera zoom" in prompt

    def test_letterbox_avoid_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "Letterboxing" in prompt or "pillarboxing" in prompt


class TestPlanPromptWhyItWorks:
    """why_it_works field should be injected so Gemini preserves viral elements."""

    def test_why_it_works_present(self, chicken_analysis, chicken_media):
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, 6)
        assert "WHY THE ORIGINAL WORKS" in prompt
        # Actual content snippet from the cached analysis
        assert "ASMR" in prompt or "satisfying" in prompt.lower()


class TestPlanPromptBeatCount:
    """Beat count in the prompt must match the argument."""

    def test_beat_count_injected(self, chicken_analysis, chicken_media):
        for bc in (3, 5, 8):
            prompt = _plan_prompt(chicken_analysis, chicken_media, 8, bc)
            assert f"Exactly {bc} beats" in prompt
