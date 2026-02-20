"""
Thumbnail Maker — generates eye-catching YouTube thumbnails using
Gemini 2.5 Flash Image (Nano Banana) and resizes with Pillow.
"""

import io
import logging
import os
from typing import Optional

from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

# YouTube recommended thumbnail size
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720


def generate_thumbnail(
    api_key: str,
    title: str,
    seo_title: str,
    output_dir: str,
    video_id: str,
) -> Optional[str]:
    """
    Generate a custom YouTube thumbnail using Gemini 2.5 Flash Image.

    Args:
        api_key: Gemini API key
        title: Original video title
        seo_title: SEO-optimized title (for text on thumbnail)
        output_dir: Directory to save the thumbnail
        video_id: Video ID (for unique filename)

    Returns:
        Path to the generated thumbnail image, or None if failed
    """
    os.makedirs(output_dir, exist_ok=True)
    client = genai.Client(api_key=api_key)

    # Create a short, punchy text for the thumbnail (max 4-5 words)
    short_text = _extract_thumbnail_text(seo_title)

    prompt = f"""Create a highly clickable, viral YouTube thumbnail for a cartoon video.

CRITICAL REQUIREMENTS:
- Center focus: EXTREMELY expressive, shocking, or funny cartoon character
- Big, bold, glowing 3D Text saying exactly: "{short_text}"
- Style: MrBeast-style YouTube thumbnail. Overly saturated colors, high contrast, glowing edges, dramatic lighting.
- The thumbnail MUST look like clickbait (but family friendly). Lots of reds, yellows, and blues.
- 16:9 aspect ratio, clean composition so it looks good on mobile phones.
- DO NOT include real photos of humans. ONLY 3D/2D animation style.
- DO NOT include watermarks or small unreadable text."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        # Check for image in response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))

                    # Resize to YouTube thumbnail dimensions
                    image = image.resize(
                        (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
                        Image.Resampling.LANCZOS,
                    )

                    # Save as JPEG
                    thumbnail_path = os.path.join(output_dir, f"thumb_{video_id}.jpg")
                    image.save(thumbnail_path, "JPEG", quality=95)

                    logger.info(f"Generated thumbnail: {thumbnail_path}")
                    return thumbnail_path

        logger.warning("No image in Gemini response, trying fallback prompt")
        return _generate_simple_thumbnail(client, short_text, output_dir, video_id)

    except Exception as e:
        logger.warning(f"Thumbnail generation failed: {e}")
        return None


def _generate_simple_thumbnail(
    client, text: str, output_dir: str, video_id: str
) -> Optional[str]:
    """Fallback: generate a simpler thumbnail if the first attempt fails."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=(
                f'Create a colorful cartoon thumbnail image with bold text "{text}". '
                "Bright colors, fun cartoon style, 16:9 ratio."
            ),
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize(
                        (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
                        Image.Resampling.LANCZOS,
                    )
                    thumbnail_path = os.path.join(output_dir, f"thumb_{video_id}.jpg")
                    image.save(thumbnail_path, "JPEG", quality=95)
                    logger.info(f"Generated fallback thumbnail: {thumbnail_path}")
                    return thumbnail_path

        return None
    except Exception as e:
        logger.warning(f"Fallback thumbnail also failed: {e}")
        return None


def _extract_thumbnail_text(title: str) -> str:
    """Extract 3-5 impactful words from the title for thumbnail text."""
    # Remove common filler words and hashtags
    skip_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "is", "are", "was", "were", "this",
        "that", "#shorts", "#meme", "#memes", "#funny", "#cartoon",
        "#animation", "#roblox", "#minecraft", "#trending", "#viral",
    }

    words = title.split()
    filtered = [w for w in words if w.lower() not in skip_words and not w.startswith("#")]

    # Take first 4 meaningful words
    result = " ".join(filtered[:4])

    # If result is too short, use original title truncated
    if len(result) < 5:
        result = title[:30]

    return result.upper()
