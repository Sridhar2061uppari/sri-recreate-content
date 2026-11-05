"""
Tests for render_prompt() – the final text pasted into Veo/Omni/Seedance.

Checks social media header, HOOK annotation, global avoids, timing line.
No API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import render_prompt, _GLOBAL_AVOID
from tests.conftest import make_mock_plan


@pytest.fixture
def chicken_prompt(chicken_media):
    plan = make_mock_plan()
    return render_prompt(plan, chicken_media, 8)


@pytest.fixture
def cats_prompt(cats_media):
    plan = make_mock_plan(beat_labels=("HOOK","BUILD","PAYOFF","CTA"), beat_durations=(1.5,2.5,2.5,1.5))
    return render_prompt(plan, cats_media, 8)


class TestSocialMediaHeader:
    """Prompt must start with SOCIAL MEDIA OPTIMISED block."""

    def test_social_header_present(self, chicken_prompt):
        assert "SOCIAL MEDIA OPTIMISED" in chicken_prompt

    def test_scroll_stopper_line(self, chicken_prompt):
        assert "scroll-stopper hook" in chicken_prompt

    def test_payoff_first_line(self, chicken_prompt):
        assert "Payoff-first structure" in chicken_prompt

    def test_no_fade_in_line(self, chicken_prompt):
        assert "No fade-in" in chicken_prompt


class TestHookSceneLabel:
    """Scene 1 must be annotated as HOOK with sound-off instruction."""

    def test_scene1_has_hook_label(self, chicken_prompt):
        # Should contain HOOK in the Scene 1 header
        lines = chicken_prompt.splitlines()
        scene1_line = next(
            (l for l in lines if l.startswith("Scene 1")), None
        )
        assert scene1_line is not None, "Scene 1 line not found"
        assert "HOOK" in scene1_line

    def test_scene1_has_sound_off_annotation(self, chicken_prompt):
        lines = chicken_prompt.splitlines()
        scene1_line = next((l for l in lines if l.startswith("Scene 1")), "")
        assert "sound-OFF" in scene1_line

    def test_scene1_has_full_energy_note(self, chicken_prompt):
        lines = chicken_prompt.splitlines()
        scene1_line = next((l for l in lines if l.startswith("Scene 1")), "")
        assert "full energy" in scene1_line

    def test_scene2_no_hook_annotation(self, chicken_prompt):
        lines = chicken_prompt.splitlines()
        scene2_line = next((l for l in lines if l.startswith("Scene 2")), "")
        assert "sound-OFF" not in scene2_line

    def test_hook_label_forced_if_missing(self, chicken_media):
        # Even if Gemini returns a different label for beat 1, HOOK is forced.
        plan = make_mock_plan(beat_labels=("INTRO", "PROCESS", "END"), beat_durations=(1.5,4.0,2.5))
        prompt = render_prompt(plan, chicken_media, 8)
        scene1_line = next((l for l in prompt.splitlines() if l.startswith("Scene 1")), "")
        assert "HOOK" in scene1_line

    def test_hook_not_duplicated_when_already_present(self, chicken_media):
        # If label is already HOOK, should not become HOOK -- HOOK
        plan = make_mock_plan(beat_labels=("HOOK", "PROCESS", "END"), beat_durations=(1.5,4.0,2.5))
        prompt = render_prompt(plan, chicken_media, 8)
        scene1_line = next((l for l in prompt.splitlines() if l.startswith("Scene 1")), "")
        assert "HOOK -- HOOK" not in scene1_line


class TestGlobalAvoids:
    """All _GLOBAL_AVOID items must appear in every prompt."""

    @pytest.mark.parametrize("avoid_item", _GLOBAL_AVOID)
    def test_global_avoid_item_present(self, chicken_prompt, avoid_item):
        assert avoid_item in chicken_prompt, (
            f"Global avoid missing: {avoid_item!r}"
        )

    def test_global_avoids_before_video_specific(self, chicken_prompt):
        avoid_idx = chicken_prompt.index("AVOID")
        first_global = chicken_prompt.index(_GLOBAL_AVOID[0])
        first_video_specific = chicken_prompt.index("Inconsistent food texture")
        assert first_global < first_video_specific, (
            "Global avoids should appear before video-specific avoids"
        )

    def test_watermarks_always_appended(self, chicken_prompt):
        assert "watermarks, platform UI, or logos" in chicken_prompt


class TestTimingFooter:
    """Timing mandatory line must still appear."""

    def test_timing_mandatory_line(self, chicken_prompt):
        assert "Timing is mandatory" in chicken_prompt

    def test_duration_in_timing_line(self, chicken_prompt):
        assert "8 seconds" in chicken_prompt

    def test_no_intro_outro(self, chicken_prompt):
        assert "intro or outro" in chicken_prompt


class TestReferenceImages:
    """Reference images block renders correctly."""

    def test_ref_block_present(self, chicken_prompt):
        assert "REFERENCE IMAGES" in chicken_prompt

    def test_ref_id_in_prompt(self, chicken_prompt):
        assert "[REF_1]" in chicken_prompt

    def test_no_ref_block_when_no_refs(self, chicken_media):
        plan = make_mock_plan(with_refs=False)
        prompt = render_prompt(plan, chicken_media, 8)
        assert "REFERENCE IMAGES" not in prompt


class TestStyleAndCharacters:

    def test_style_section_present(self, chicken_prompt):
        assert "STYLE" in chicken_prompt

    def test_characters_section_present(self, chicken_prompt):
        assert "CHARACTERS" in chicken_prompt

    def test_timeline_section_present(self, chicken_prompt):
        assert "TIMELINE" in chicken_prompt
