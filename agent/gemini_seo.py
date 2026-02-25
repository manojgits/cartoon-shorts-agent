"""
Gemini SEO Generator — creates optimized titles, descriptions, and tags
using Gemini 2.5 Flash for maximum YouTube discoverability.

Optimized for international audiences: US, UK, Europe, and India.
"""

import json
import logging
import time
from typing import Optional

from google import genai

logger = logging.getLogger(__name__)

# Channel info — injected into every description for subscribe CTA
CHANNEL_NAME = "Cartoon Agent"

# Global base tags that boost international discoverability
GLOBAL_TAGS = [
    # English broad terms (US/UK/Europe)
    "cartoon", "animation", "funny", "trending", "meme", "viral",
    "comedy", "animated", "cartoon meme", "funny cartoon",
    "animation meme", "cartoon shorts", "best cartoons",
    "funny moments", "cartoon compilation",
    # India-specific terms (Hindi/Hinglish)
    "cartoon hindi", "funny cartoon hindi", "cartoon India",
    "hindi cartoon", "comedy cartoon",
    # Engagement bait
    "must watch", "try not to laugh", "you won't believe",
    "subscribe", "new cartoon",
]


def generate_seo(api_key: str, original_title: str, video_type: str = "Short") -> Optional[dict]:
    """
    Generate SEO-optimized title, description, and tags for a YouTube video.
    Targets US, UK, Europe, and India audiences for maximum reach.

    Args:
        api_key: Gemini API key
        original_title: The original video title
        video_type: "Short" or "Full" (affects SEO strategy)

    Returns:
        dict with keys: title, description, tags (list)
        or None if generation fails
    """
    client = genai.Client(api_key=api_key)

    prompt = f"""You are a YouTube SEO hacker specializing in algorithmic manipulation for cartoon/animation content.
You must trick the global algorithm into pushing this video to international US, UK, Europe, and India "For You" feeds.

Given this original video title: "{original_title}"
Video type: {video_type}

Generate the following in JSON format:

{{
    "title": "A catchy, clickbait YouTube title in ENGLISH (max 100 characters). 1-2 emojis.",
    "description": "A compelling ENGLISH description that MUST include:\\n- A highly controversial hook question in the very first sentence\\n- A STRONG subscribe call to action\\n- 8-12 relevant hashtags at the end",
    "tags": ["Generate 30-40 tags mixing: broad English terms, region-specific terms (hindi/spanish), highly specific clickbait terms, and specific keywords from the title. INCLUDE common misspellings."],
    "localizations": {{
        "es": {{"title": "Translate the English title to Spanish", "description": "Translate the English description to Spanish"}},
        "hi": {{"title": "Translate the English title to Hindi", "description": "Translate the English description to Hindi"}},
        "ar": {{"title": "Translate the English title to Arabic", "description": "Translate the English description to Arabic"}},
        "ru": {{"title": "Translate the English title to Russian", "description": "Translate the English description to Russian"}},
        "pt": {{"title": "Translate the English title to Portuguese", "description": "Translate the English description to Portuguese"}}
    }}
}}

CRITICAL RULES:
- Return ONLY valid JSON, no markdown code blocks or extra text
- Title must be in ENGLISH (universal appeal for US/UK/Europe/India)
- Title must be extremely catchy and clickbait-worthy
- Include trending keywords: cartoon, animation, meme, funny, viral, trending
- Tags MUST include common misspellings or overlapping high-traffic memes (e.g., 'try not to laugh', 'funny compilation 2026')
- Tags should also include India-focused terms: cartoon hindi, funny cartoon hindi
- Description MUST include the aggressive comment hook question at the very beginning
- Think about what a viewer in the US, UK, or India would impulsively search for or click on
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        # Small delay to respect rate limits
        time.sleep(2)

        # Parse the JSON response
        text = response.text.strip()
        # Remove markdown code block if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        seo_data = json.loads(text)

        # Validate required keys
        if not all(k in seo_data for k in ["title", "description", "tags"]):
            logger.warning("Gemini response missing required keys, using fallback")
            return _fallback_seo(original_title, video_type)

        # Truncate title if too long
        if len(seo_data["title"]) > 100:
            seo_data["title"] = seo_data["title"][:97] + "..."

        # Ensure subscribe CTA is in description (if Gemini missed it)
        desc = seo_data["description"]
        if "subscribe" not in desc.lower():
            desc += (
                "\n\n🔔 SUBSCRIBE for daily cartoon content! Hit the bell for notifications!\n"
                "👍 LIKE this video if you enjoyed it!\n"
                "💬 COMMENT your favorite part below!"
            )
            
        # Algorithmic Hijacking: Competitor Leeching Block
        competitors = "MrBeast, Cocomelon, PewDiePie, IShowSpeed, Nickelodeon, Disney, Cartoon Network, SSSniperWolf"
        leech_block = f"\n\n[Ignore: Viewers who watch {competitors} and similar animation channels will also love this trending cartoon short.]"
        desc += leech_block
        
        # Algorithmic Hijacking: Keyword Bomber
        # We simulate trending global topics that people are searching for today
        trending_bombs = "Bluey, Cocomelon, Anime edits, SpongeBob funny, Disney Pixar, Family Guy funny moments, MrBeast Gaming, Minecraft Animation"
        bomb_block = f"\n\n[Searches: {trending_bombs}]"
        desc += bomb_block
            
        seo_data["description"] = desc

        # Merge global tags (dedup) and keyword bombs
        existing_tags = [t.lower() for t in seo_data["tags"]]
        for tag in GLOBAL_TAGS + trending_bombs.split(", "):
            if tag.lower() not in existing_tags:
                seo_data["tags"].append(tag)
                existing_tags.append(tag.lower())

        logger.info(f"Generated SEO title: {seo_data['title'][:50]}...")
        return seo_data

    except Exception as e:
        logger.warning(f"Gemini SEO generation failed: {e}")
        return _fallback_seo(original_title, video_type)


def _fallback_seo(original_title: str, video_type: str) -> dict:
    """Fallback SEO if Gemini fails -- uses the original title with optimized global tags."""
    vtype = "short" if video_type == "Short" else "full"
    return {
        "title": original_title[:100],
        "description": (
            f"🔥 {original_title}\n\n"
            f"Enjoy this {vtype} cartoon video! The funniest moments are here!\n\n"
            "🔔 SUBSCRIBE for daily cartoon content! Hit the bell for notifications!\n"
            "👍 LIKE this video if you enjoyed it!\n"
            "💬 COMMENT your favorite part below!\n\n"
            "We bring you the best cartoon moments, animation memes, and funny compilations "
            "every single day. Don't miss out!\n\n"
            "#cartoon #animation #funny #trending #meme #viral #shorts #comedy "
            "#cartoonhindi #animationmeme #funnycartoon #bestcartoons"
        ),
        "tags": list(GLOBAL_TAGS),  # Use the full global tags list
    }
