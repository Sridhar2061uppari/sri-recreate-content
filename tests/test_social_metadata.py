"""
test_social_metadata.py - Tests for the SocialMetadata feature.
Covers: schema validation, _trim_tags, _validate_instagram_hashtags,
render_social_metadata, GeneratedPrompt.full_text with social section.
Zero API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_video import (
    SocialMetadata, _trim_tags, _validate_instagram_hashtags,
    render_social_metadata, GeneratedPrompt,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_meta():
    return SocialMetadata(
        youtube_title="Phones in 2070 dropped this (wait for it)",
        youtube_description=(
            "What if your phone could save itself? Futuristic thruster tech meets "
            "everyday clumsy moments. Technology in 2070 hits different fr."
        ),
        youtube_tags=(
            "phone drop, futuristic technology, phone thrusters, tech memes, "
            "viral shorts, funny moments, satisfying videos, trending"
        ),
        instagram_caption="bro saved his phone",
        instagram_hashtags="#phonedrop #futuretech #techfail #viral #reels #explorepage",
    )


@pytest.fixture
def mock_generated_prompt(mock_meta):
    social_text = render_social_metadata(mock_meta)
    return GeneratedPrompt(
        duration=8,
        prompt="Mock video prompt text.",
        plan={},
        saved_to="test.txt",
        reference_sheet="",
        social_metadata=mock_meta,
        social_text=social_text,
    )


# ── YouTube character limits ─────────────────────────────────────────────────

class TestYouTubeCharacterLimits:

    def test_youtube_title_under_100_chars(self, mock_meta):
        assert len(mock_meta.youtube_title) <= 100, (
            f"Title too long: {len(mock_meta.youtube_title)} chars"
        )

    def test_youtube_tags_under_450_chars(self, mock_meta):
        assert len(mock_meta.youtube_tags) <= 450, (
            f"Tags too long: {len(mock_meta.youtube_tags)} chars (limit 450)"
        )

    def test_youtube_description_under_500_chars(self, mock_meta):
        assert len(mock_meta.youtube_description) <= 500

    def test_youtube_tags_no_hash_symbols(self, mock_meta):
        assert "#" not in mock_meta.youtube_tags, (
            "YouTube tags must not contain # symbols"
        )

    def test_youtube_tags_comma_separated(self, mock_meta):
        parts = [t.strip() for t in mock_meta.youtube_tags.split(",") if t.strip()]
        assert len(parts) >= 3, "Need at least 3 comma-separated tags"


# ── Instagram format ─────────────────────────────────────────────────────────

class TestInstagramFormat:

    def test_instagram_caption_max_5_words(self, mock_meta):
        word_count = len(mock_meta.instagram_caption.split())
        assert word_count <= 5, (
            f"Caption has {word_count} words (limit 5): {mock_meta.instagram_caption!r}"
        )

    def test_instagram_hashtags_all_start_with_hash(self, mock_meta):
        tokens = mock_meta.instagram_hashtags.split()
        for t in tokens:
            assert t.startswith("#"), f"Hashtag missing #: {t!r}"

    def test_instagram_has_viral(self, mock_meta):
        lower = mock_meta.instagram_hashtags.lower()
        assert "#viral" in lower

    def test_instagram_has_reels(self, mock_meta):
        lower = mock_meta.instagram_hashtags.lower()
        assert "#reels" in lower

    def test_instagram_has_explorepage(self, mock_meta):
        lower = mock_meta.instagram_hashtags.lower()
        assert "#explorepage" in lower

    def test_instagram_total_hashtags_5_to_6(self, mock_meta):
        count = len(mock_meta.instagram_hashtags.split())
        assert 5 <= count <= 6, (
            f"Expected 5-6 hashtags, got {count}: {mock_meta.instagram_hashtags}"
        )


# ── _trim_tags helper ────────────────────────────────────────────────────────

class TestTrimTags:

    def test_short_tags_unchanged(self):
        tags = "phone drop, tech memes, viral shorts"
        assert _trim_tags(tags, 450) == tags

    def test_long_tags_trimmed_to_limit(self):
        long = ", ".join(["tag number " + str(i) for i in range(100)])
        result = _trim_tags(long, 450)
        assert len(result) <= 450

    def test_trimmed_result_ends_at_full_tag(self):
        """Result must end at a complete tag, not mid-word."""
        long = ", ".join(["word" + str(i) for i in range(100)])
        result = _trim_tags(long, 450)
        # Should not end with a partial comma
        assert not result.endswith(",")

    def test_empty_string_unchanged(self):
        assert _trim_tags("", 450) == ""


# ── _validate_instagram_hashtags helper ─────────────────────────────────────

class TestValidateInstagramHashtags:

    def test_adds_missing_hash_prefix(self):
        result = _validate_instagram_hashtags("phonedrop futuretech")
        assert "#phonedrop" in result
        assert "#futuretech" in result

    def test_keeps_existing_hashes(self):
        result = _validate_instagram_hashtags("#phonedrop #futuretech")
        assert result.count("#phonedrop") == 1  # no duplication

    def test_adds_viral_if_missing(self):
        result = _validate_instagram_hashtags("#phonedrop #futuretech #reels #explorepage")
        assert "#viral" in result.lower()

    def test_adds_reels_if_missing(self):
        result = _validate_instagram_hashtags("#phonedrop #viral #explorepage")
        assert "#reels" in result.lower()

    def test_adds_explorepage_if_missing(self):
        result = _validate_instagram_hashtags("#phonedrop #viral #reels")
        assert "#explorepage" in result.lower()

    def test_caps_at_6_hashtags(self):
        many = " ".join(["#tag" + str(i) for i in range(20)])
        result = _validate_instagram_hashtags(many)
        assert len(result.split()) <= 6


# ── render_social_metadata output ────────────────────────────────────────────

class TestRenderSocialMetadata:

    def test_youtube_section_header_present(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert "=== YOUTUBE ===" in text

    def test_instagram_section_header_present(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert "=== INSTAGRAM ===" in text

    def test_title_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert mock_meta.youtube_title in text

    def test_description_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert mock_meta.youtube_description in text

    def test_tags_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert mock_meta.youtube_tags in text

    def test_tags_char_count_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert "/450" in text

    def test_caption_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert mock_meta.instagram_caption in text

    def test_hashtags_in_output(self, mock_meta):
        text = render_social_metadata(mock_meta)
        assert mock_meta.instagram_hashtags in text


# ── GeneratedPrompt.full_text includes social section ────────────────────────

class TestGeneratedPromptFullText:

    def test_full_text_includes_social_section(self, mock_generated_prompt):
        full = mock_generated_prompt.full_text()
        assert "=== SOCIAL MEDIA METADATA ===" in full

    def test_full_text_includes_youtube(self, mock_generated_prompt):
        full = mock_generated_prompt.full_text()
        assert "=== YOUTUBE ===" in full

    def test_full_text_includes_instagram(self, mock_generated_prompt):
        full = mock_generated_prompt.full_text()
        assert "=== INSTAGRAM ===" in full

    def test_full_text_without_social_no_section(self):
        gp = GeneratedPrompt(
            duration=8, prompt="Test prompt.", plan={},
            saved_to="test.txt", reference_sheet="",
        )
        full = gp.full_text()
        assert "=== SOCIAL MEDIA METADATA ===" not in full

    def test_no_api_calls(self):
        import recreate_video as rv
        assert rv._STATE.client is None
