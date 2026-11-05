"""
End-to-end hook structure test.

Simulates the full flow: cached analysis -> _plan_prompt text ->
mock RecreationPlan -> render_prompt -> check final output for all
viral/social-media requirements.
No API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import (
    _plan_prompt, render_prompt, beats_for_duration,
    VideoAnalysis, MediaInfo, _GLOBAL_AVOID,
)
from tests.conftest import make_mock_plan


class TestPlanPromptHookRulesEndToEnd:
    """_plan_prompt must embed all hook constraints for Gemini."""

    def test_chicken_prompt_has_hook_first_section(self, chicken_analysis, chicken_media):
        bc = beats_for_duration(8, len(chicken_analysis.scenes))
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, bc)
        required = [
            "HOOK-FIRST STRUCTURE",
            "Beat 1 label MUST be",
            "AUDIO MUTED",
            "scroll-stopper",
            "CTA frame",
        ]
        for phrase in required:
            assert phrase in prompt, f"Missing required phrase: {phrase!r}"

    def test_cats_prompt_includes_hook_analysis(self, cats_analysis, cats_media):
        bc = beats_for_duration(8, len(cats_analysis.scenes))
        prompt = _plan_prompt(cats_analysis, cats_media, 8, bc)
        assert cats_analysis.hook[:30] in prompt

    def test_why_it_works_injected(self, chicken_analysis, chicken_media):
        bc = beats_for_duration(8, len(chicken_analysis.scenes))
        prompt = _plan_prompt(chicken_analysis, chicken_media, 8, bc)
        assert "WHY THE ORIGINAL WORKS" in prompt
        assert chicken_analysis.why_it_works[:40] in prompt


class TestRenderPromptHookEndToEnd:
    """render_prompt output checked for all social/hook requirements."""

    def get_prompt(self, media, beats=3):
        labels = ("HOOK", "PROCESS", "PAYOFF")[:beats]
        durs_map = {2: (1.5, 6.5), 3: (1.5, 4.0, 2.5), 4: (1.5, 2.5, 2.5, 1.5)}
        durs = durs_map.get(beats, (1.5, 4.0, 2.5))
        plan = make_mock_plan(beat_labels=labels[:beats], beat_durations=durs[:beats])
        return render_prompt(plan, media, 8)

    def test_social_header_in_output(self, chicken_media):
        p = self.get_prompt(chicken_media)
        assert "SOCIAL MEDIA OPTIMISED" in p

    def test_scene1_hook_label(self, chicken_media):
        p = self.get_prompt(chicken_media)
        s1 = next(l for l in p.splitlines() if l.startswith("Scene 1"))
        assert "HOOK" in s1

    def test_scene1_sound_off(self, chicken_media):
        p = self.get_prompt(chicken_media)
        s1 = next(l for l in p.splitlines() if l.startswith("Scene 1"))
        assert "sound-OFF" in s1

    def test_all_global_avoids_present(self, chicken_media):
        p = self.get_prompt(chicken_media)
        for item in _GLOBAL_AVOID:
            assert item in p, f"Global avoid missing: {item!r}"

    def test_timing_footer_present(self, chicken_media):
        p = self.get_prompt(chicken_media)
        assert "Timing is mandatory" in p
        assert "8 seconds" in p

    def test_works_for_cats_video(self, cats_media):
        p = self.get_prompt(cats_media, beats=4)
        assert "SOCIAL MEDIA OPTIMISED" in p
        assert "HOOK" in next(l for l in p.splitlines() if l.startswith("Scene 1"))


class TestNoRealAPICallsMade:
    """Sanity: confirm tests never imported anything that triggers the API."""

    def test_no_genai_client_created(self):
        import recreate_video as rv
        # _STATE.client should still be None since no API calls were made.
        assert rv._STATE.client is None, (
            "A real Gemini client was created during tests -- API calls may have occurred!"
        )
