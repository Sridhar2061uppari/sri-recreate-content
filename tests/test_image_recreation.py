"""
test_image_recreation.py - Tests for recreate_image.py.
Covers: schema validation, render output, text overlay preservation,
audio fields, download media type detection, full_text social section.
Zero API calls.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from recreate_image import (
    TextOverlay, SuggestedAudio, ImageAnalysis, ImageRecreationPlan,
    GeneratedImagePrompt, SUPPORTED_IMAGE_SUFFIXES,
    render_image_prompts, render_audio_section,
)
import recreate_image as ri


# ── Shared fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def mock_audio():
    return SuggestedAudio(
        track_name="Calm Down",
        artist_name="Rema ft. Selena Gomez",
        instagram_search_query="Calm Down Rema Selena Gomez",
        mood_match="Upbeat afrobeats matches vibrant visual energy",
        genre="afrobeats",
        bpm_feel="mid-tempo energetic",
        alternative_track_name="As It Was",
        alternative_artist_name="Harry Styles",
        alternative_search_query="As It Was Harry Styles",
    )


@pytest.fixture
def mock_overlay():
    return TextOverlay(
        text="Phones in 2070:",
        position="top-center",
        style="bold white sans-serif with black drop shadow",
        purpose="meme caption",
        canva_instruction="Add white bold heading text box at top, font size 80",
    )


@pytest.fixture
def mock_analysis_with_text(mock_audio, mock_overlay):
    return ImageAnalysis(
        summary="A viral meme about futuristic smartphones.",
        hook="Surprising concept of phones with rocket thrusters.",
        why_it_works="Tech memes with unexpected concepts go viral easily.",
        content_type="meme",
        visual_medium="photography",
        subject="Black smartphone with thruster nozzles on corners, hovering above floor.",
        composition="centered subject, low angle shot",
        color_palette="dark background, silver and black phone",
        lighting="dramatic studio side-light",
        background="plain white floor, dark gradient background",
        has_text=True,
        text_overlays=[mock_overlay],
        mood="humorous and surprising",
        aspect_ratio="9:16",
        suggested_audio=mock_audio,
    )


@pytest.fixture
def mock_analysis_no_text(mock_audio):
    return ImageAnalysis(
        summary="An aesthetic lifestyle shot.",
        hook="Golden hour lighting with a stunning subject.",
        why_it_works="Aesthetic images with warm tones perform well.",
        content_type="aesthetic",
        visual_medium="photography",
        subject="Woman in a field at golden hour.",
        composition="rule of thirds",
        color_palette="warm earth tones, burnt orange, golden yellow",
        lighting="natural golden hour side-light",
        background="blurred wheat field",
        has_text=False,
        text_overlays=[],
        mood="warm and peaceful",
        aspect_ratio="9:16",
        suggested_audio=mock_audio,
    )


@pytest.fixture
def mock_plan_with_text(mock_audio, mock_overlay):
    return ImageRecreationPlan(
        title="Futuristic phone meme",
        logline="A meme showing smartphones with rocket thrusters in 2070.",
        nano_banana_prompt=(
            "black smartphone with small rocket thrusters on corners hovering above white floor, "
            "low angle shot, dramatic studio lighting, photorealistic, cinematic, 8k"
        ),
        flux_midjourney_prompt=(
            "black smartphone with rocket thrusters hovering, photorealistic, "
            "dramatic lighting --ar 9:16 --q 2 --style raw"
        ),
        stable_diffusion_prompt=(
            "black smartphone, rocket thrusters, hovering, masterpiece, best quality, "
            "ultra-detailed, photorealistic, 8k, dramatic lighting"
        ),
        negative_prompt=(
            "blurry, low quality, watermark, text, logo, ugly, deformed, "
            "extra limbs, bad anatomy, nsfw"
        ),
        text_overlays=[mock_overlay],
        canva_workflow=(
            "1. Create 9:16 canvas (1080x1920px).\n"
            "2. Set generated image as full background.\n"
            "3. Add white bold heading text at top: font size 80, no fill, black drop shadow."
        ),
        suggested_audio=mock_audio,
        aspect_ratio="9:16",
        avoid=["modern phone style", "wrong phone design", "missing thrusters"],
    )


@pytest.fixture
def mock_plan_no_text(mock_audio):
    return ImageRecreationPlan(
        title="Golden hour lifestyle",
        logline="Aesthetic lifestyle photo at golden hour.",
        nano_banana_prompt="woman in wheat field at golden hour, warm tones, photorealistic",
        flux_midjourney_prompt="woman wheat field golden hour --ar 9:16 --q 2 --style raw",
        stable_diffusion_prompt="woman in field, golden hour, masterpiece, best quality, 8k",
        negative_prompt="blurry, low quality, watermark, text, ugly",
        text_overlays=[],
        canva_workflow="No text overlays needed.",
        suggested_audio=mock_audio,
        aspect_ratio="9:16",
        avoid=["wrong lighting", "cold tones"],
    )


# ── SuggestedAudio ───────────────────────────────────────────────────────────

class TestSuggestedAudio:

    def test_track_name_not_empty(self, mock_audio):
        assert mock_audio.track_name

    def test_artist_name_not_empty(self, mock_audio):
        assert mock_audio.artist_name

    def test_instagram_search_query_not_empty(self, mock_audio):
        assert mock_audio.instagram_search_query

    def test_alternative_track_not_empty(self, mock_audio):
        assert mock_audio.alternative_track_name

    def test_alternative_search_query_not_empty(self, mock_audio):
        assert mock_audio.alternative_search_query

    def test_mood_match_not_empty(self, mock_audio):
        assert mock_audio.mood_match

    def test_genre_not_empty(self, mock_audio):
        assert mock_audio.genre


# ── TextOverlay ───────────────────────────────────────────────────────────────

class TestTextOverlay:

    def test_text_not_empty(self, mock_overlay):
        assert mock_overlay.text

    def test_position_not_empty(self, mock_overlay):
        assert mock_overlay.position

    def test_canva_instruction_not_empty(self, mock_overlay):
        assert mock_overlay.canva_instruction

    def test_style_not_empty(self, mock_overlay):
        assert mock_overlay.style


# ── render_audio_section ──────────────────────────────────────────────────────

class TestRenderAudioSection:

    def test_track_name_in_output(self, mock_audio):
        text = render_audio_section(mock_audio)
        assert mock_audio.track_name in text

    def test_artist_in_output(self, mock_audio):
        text = render_audio_section(mock_audio)
        assert mock_audio.artist_name in text

    def test_search_query_in_output(self, mock_audio):
        text = render_audio_section(mock_audio)
        assert mock_audio.instagram_search_query in text

    def test_alternative_track_in_output(self, mock_audio):
        text = render_audio_section(mock_audio)
        assert mock_audio.alternative_track_name in text

    def test_recommended_audio_header(self, mock_audio):
        text = render_audio_section(mock_audio)
        assert "RECOMMENDED AUDIO" in text


# ── render_image_prompts: all sections present ────────────────────────────────

class TestRenderImagePromptsAllSections:

    def test_nano_banana_section(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "NANO BANANA" in text

    def test_flux_section(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "FLUX" in text

    def test_stable_diffusion_section(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "STABLE DIFFUSION" in text

    def test_negative_prompt_section(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "NEGATIVE PROMPT" in text

    def test_audio_section(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "RECOMMENDED AUDIO" in text

    def test_nano_banana_prompt_content(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert mock_plan_with_text.nano_banana_prompt in text

    def test_negative_prompt_content(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "blurry" in text


# ── Text overlay preservation ─────────────────────────────────────────────────

class TestTextOverlayPreservation:

    def test_text_overlay_section_present_when_has_text(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "TEXT OVERLAYS" in text

    def test_original_text_content_preserved(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "Phones in 2070" in text

    def test_canva_workflow_present_when_has_text(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        assert "Canva" in text or "CapCut" in text

    def test_text_overlay_no_section_when_no_text(self, mock_plan_no_text, mock_analysis_no_text):
        text = render_image_prompts(mock_plan_no_text, mock_analysis_no_text)
        # Should say no overlays needed, not the full Canva workflow
        assert "No text overlays" in text

    def test_no_text_flag_false_means_empty_overlays(self, mock_analysis_no_text):
        assert mock_analysis_no_text.has_text is False
        assert mock_analysis_no_text.text_overlays == []


# ── SUPPORTED_IMAGE_SUFFIXES ──────────────────────────────────────────────────

class TestSupportedImageSuffixes:

    def test_jpg_in_suffixes(self):
        assert ".jpg" in SUPPORTED_IMAGE_SUFFIXES

    def test_jpeg_in_suffixes(self):
        assert ".jpeg" in SUPPORTED_IMAGE_SUFFIXES

    def test_png_in_suffixes(self):
        assert ".png" in SUPPORTED_IMAGE_SUFFIXES

    def test_webp_in_suffixes(self):
        assert ".webp" in SUPPORTED_IMAGE_SUFFIXES

    def test_mp4_not_in_image_suffixes(self):
        assert ".mp4" not in SUPPORTED_IMAGE_SUFFIXES

    def test_webm_not_in_image_suffixes(self):
        assert ".webm" not in SUPPORTED_IMAGE_SUFFIXES


# ── GeneratedImagePrompt.full_text ────────────────────────────────────────────

class TestGeneratedImagePromptFullText:

    def test_full_text_includes_prompt(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        gp = GeneratedImagePrompt(
            prompt_text=text, plan=mock_plan_with_text.model_dump(),
            social_text="SOCIAL SECTION", social_metadata=None, saved_to="test.txt",
        )
        full = gp.full_text()
        assert "NANO BANANA" in full

    def test_full_text_includes_social_when_present(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        gp = GeneratedImagePrompt(
            prompt_text=text, plan=mock_plan_with_text.model_dump(),
            social_text="SOCIAL SECTION", social_metadata=None, saved_to="test.txt",
        )
        full = gp.full_text()
        assert "SOCIAL MEDIA METADATA" in full

    def test_full_text_no_social_section_when_empty(self, mock_plan_with_text, mock_analysis_with_text):
        text = render_image_prompts(mock_plan_with_text, mock_analysis_with_text)
        gp = GeneratedImagePrompt(
            prompt_text=text, plan=mock_plan_with_text.model_dump(),
            social_text="", social_metadata=None, saved_to="test.txt",
        )
        full = gp.full_text()
        assert "SOCIAL MEDIA METADATA" not in full

    def test_no_api_calls(self):
        import recreate_video as rv
        assert rv._STATE.client is None
