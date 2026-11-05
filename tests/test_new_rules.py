"""Tests for the 4 new rules after smartphone thruster video analysis.
No API calls - uses cached analysis data.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recreate_video import _plan_prompt, render_prompt, beats_for_duration, _GLOBAL_AVOID
from tests.conftest import make_mock_plan


def get_plan_prompt(analysis, media, duration=8):
    bc = beats_for_duration(duration, len(analysis.scenes))
    return _plan_prompt(analysis, media, duration, bc)


class TestNoTextRuleInPlanPrompt:

    def test_no_text_section_present(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "NO TEXT RULE" in p

    def test_on_screen_text_must_be_empty_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "on_screen_text MUST be empty" in p

    def test_do_not_reproduce_overlays_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "Do NOT reproduce any text overlays" in p

    def test_meme_caption_text_mentioned(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "meme text" in p or "caption text" in p

    def test_cats_video_has_no_text_rule(self, cats_analysis, cats_media):
        p = get_plan_prompt(cats_analysis, cats_media)
        assert "NO TEXT RULE" in p

    def test_no_text_in_avoid_section(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "On-screen text, captions, subtitles" in p


class TestNoTextRuleInGlobalAvoid:

    def test_no_text_item_in_global_avoid(self):
        has_text_rule = any(
            "text" in item.lower() or "caption" in item.lower() or "subtitle" in item.lower()
            for item in _GLOBAL_AVOID
        )
        assert has_text_rule, f"No text/caption rule in _GLOBAL_AVOID: {_GLOBAL_AVOID}"

    def test_text_free_phrase_in_global_avoid(self):
        assert any("text-free" in item for item in _GLOBAL_AVOID)


class TestNoTextRuleInRenderPrompt:

    def test_no_text_avoid_in_final_prompt(self, chicken_media):
        plan = make_mock_plan()
        prompt = render_prompt(plan, chicken_media, 8)
        assert any("text" in item.lower() and item in prompt for item in _GLOBAL_AVOID)

    def test_on_screen_text_line_suppressed_when_empty(self, chicken_media):
        plan = make_mock_plan()
        prompt = render_prompt(plan, chicken_media, 8)
        assert "On-screen text:" not in prompt


class TestSettingConsistencyInPlanPrompt:

    def test_setting_consistency_section_present(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "SETTING CONSISTENCY" in p

    def test_identical_room_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "EXACT same room" in p or "identical setting" in p.lower()

    def test_no_floor_change_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "floor type" in p

    def test_setting_consistency_in_avoid(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "Changing room" in p or "identical setting" in p


class TestSettingConsistencyInGlobalAvoid:

    def test_setting_change_in_global_avoid(self):
        has_setting_rule = any(
            "setting" in item.lower() or "background" in item.lower() or "room" in item.lower()
            for item in _GLOBAL_AVOID
        )
        assert has_setting_rule, f"No setting rule in _GLOBAL_AVOID: {_GLOBAL_AVOID}"


class TestPhysicsPrecisionInPlanPrompt:

    def test_physics_section_present(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "PHYSICS" in p

    def test_start_end_state_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "START" in p and "END" in p

    def test_orientation_instruction(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "orientation" in p or "tilt angle" in p


class TestRefImagePhysicalPrecision:

    def test_physical_precision_in_plan(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "physical precision" in p or "exact orientation" in p

    def test_face_orientation_examples(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "face-up" in p or "face-down" in p or "horizontal" in p

    def test_avoid_includes_wrong_orientation(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        assert "orientation" in p


class TestAllNewRulesCombined:

    REQUIRED = ["NO TEXT RULE", "SETTING CONSISTENCY", "PHYSICS", "physical precision"]

    def test_all_rules_present_chicken(self, chicken_analysis, chicken_media):
        p = get_plan_prompt(chicken_analysis, chicken_media)
        for phrase in self.REQUIRED:
            assert phrase in p, f"Missing: {phrase!r}"

    def test_all_rules_present_cats(self, cats_analysis, cats_media):
        p = get_plan_prompt(cats_analysis, cats_media)
        for phrase in self.REQUIRED:
            assert phrase in p, f"Missing (cats): {phrase!r}"

    def test_global_avoid_has_7_items(self):
        assert len(_GLOBAL_AVOID) == 7, f"Expected 7 items, got {len(_GLOBAL_AVOID)}: {_GLOBAL_AVOID}"

    def test_no_api_calls(self):
        import recreate_video as rv
        assert rv._STATE.client is None
