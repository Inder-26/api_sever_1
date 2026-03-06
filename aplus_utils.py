"""
Amazon A+ Banner Generation Utilities
======================================
Helper functions for theme generation, text generation, and banner processing
for A+ content creation.
"""

import json
import re
import io
import base64
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from PIL import Image

from aplus_prompts import (
    APLUS_THEME_GENERATION_PROMPT,
    APLUS_TEXT_GENERATION_PROMPT,
    APLUS_BANNER_TYPES,
    get_aplus_banner_prompt,
    get_aplus_text_prompt
)

# ============================================================================
# THEME GENERATION
# ============================================================================

def generate_aplus_theme(image_bytes: bytes) -> Dict[str, Any]:
    """
    Generate a universal theme for earring images across all 4 A+ banners.
    
    Uses vision analysis to determine:
    - Metal tone (gold, silver, rose gold, oxidised, antique)
    - Primary colors and mood
    - Background color that complements the earring
    - Typography color and style
    - Lighting mood
    
    Args:
        image_bytes: Raw image bytes of earring image
        
    Returns:
        Dict containing:
        {
            "earring_style": str,
            "metal_tone": str,
            "primary_colors": List[str],
            "mood": str,
            "background_color": str (#HEX format),
            "background_description": str,
            "texture_pattern": str,
            "border_style": str,
            "typography_color": str,
            "typography_style": str,
            "lighting_mood": str,
            "theme_line": "Formatted string for use in prompts"
        }
    """
    
    import base64
    from openai import OpenAI
    
    try:
        # Use OpenAI GPT-4o mini for vision analysis (free tier available)
        client = OpenAI()
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call GPT-4o mini with vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": APLUS_THEME_GENERATION_PROMPT
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=500
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content
        
        # Try to parse JSON
        try:
            theme_dict = json.loads(response_text)
            return theme_dict
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                theme_dict = json.loads(json_match.group())
                return theme_dict
            else:
                # Return default theme if parsing fails
                return get_default_theme()
                
    except Exception as e:
        print(f"Error generating theme: {str(e)}")
        return get_default_theme()


def get_default_theme() -> Dict[str, Any]:
    """Return a default luxurious theme for fallback."""
    return {
        "earring_style": "elegant jhumka",
        "metal_tone": "gold",
        "primary_colors": ["deep maroon", "gold"],
        "mood": "royal festive",
        "background_color": "#1a1a1a",
        "background_description": "deep charcoal with subtle gold texture",
        "texture_pattern": "subtle damask pattern",
        "border_style": "ornate gold border",
        "typography_color": "ivory",
        "typography_style": "serif",
        "lighting_mood": "warm amber spotlight",
        "theme_line": "Deep maroon #1a1a1a | subtle damask | ornate gold | ivory serif | warm spotlight"
    }


# ============================================================================
# TEXT GENERATION FOR A+ BANNERS
# ============================================================================

def generate_aplus_banner_text(
    image_bytes: bytes,
    banner_type_index: int,
    theme_dict: Dict[str, Any],
    earring_description: str = ""
) -> Dict[str, Any]:
    """
    Generate dynamic text content for a specific A+ banner type.
    
    Uses GPT-4o mini vision to analyze earring and create contextual text
    that matches the banner type and universal theme.
    
    Args:
        image_bytes: Raw image bytes of earring
        banner_type_index: 0=Hero, 1=Model Wearing, 2=Front & Back, 3=Care Tips
        theme_dict: Theme dictionary from generate_aplus_theme()
        earring_description: Optional pre-analyzed earring description
        
    Returns:
        Dict containing:
        {
            "prompt_index": int,
            "image_type_name": str,
            "heading": str,
            "subheading": str,
            "bullets": List[str],
            "theme_line": str
        }
    """
    
    import base64
    from openai import OpenAI
    
    # Care Tips banner has pre-defined text
    if banner_type_index == 3:
        return {
            "prompt_index": 3,
            "image_type_name": APLUS_BANNER_TYPES[3]["name"],
            "heading": "Care & Storage Tips",
            "subheading": "Maintain Your Treasure",
            "bullets": [
                "Store in a safe dry place when not in use",
                "Avoid contact with water, perfume & chemicals",
                "Wipe gently with a soft dry cloth",
                "Keep away from direct sunlight & heat"
            ],
            "theme_line": theme_dict.get("theme_line", "")
        }
    
    # Front & Back banner is visual-only, minimal text
    if banner_type_index == 2:
        banner_name = APLUS_BANNER_TYPES[2]["name"]
        metal_tone = theme_dict.get("metal_tone", "gold")
        
        return {
            "prompt_index": 2,
            "image_type_name": banner_name,
            "heading": f"Front & Back\nDesign Detail",
            "subheading": "Exquisite Craftsmanship",
            "bullets": [
                "Stunning front view with intricate details",
                "Beautiful back design for complete beauty"
            ],
            "theme_line": theme_dict.get("theme_line", "")
        }
    
    try:
        client = OpenAI()
        
        # Encode image
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Build earring details context
        if not earring_description:
            earring_details = "Analyze the earring style, materials, and aesthetic from the image."
        else:
            earring_details = earring_description
        
        # Get appropriate prompt
        text_prompt = get_aplus_text_prompt(banner_type_index, theme_dict, earring_details)
        
        # Call GPT-4o mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": text_prompt
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=300
        )
        
        # Parse response
        response_text = response.choices[0].message.content
        
        try:
            text_dict = json.loads(response_text)
            return text_dict
        except json.JSONDecodeError:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                text_dict = json.loads(json_match.group())
                return text_dict
            else:
                return get_default_banner_text(banner_type_index, theme_dict)
                
    except Exception as e:
        print(f"Error generating banner text: {str(e)}")
        return get_default_banner_text(banner_type_index, theme_dict)


def get_default_banner_text(banner_type_index: int, theme_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return default text for a banner type."""
    
    defaults = {
        0: {  # Hero
            "prompt_index": 0,
            "image_type_name": APLUS_BANNER_TYPES[0]["name"],
            "heading": "Timeless Elegance\nRedefined",
            "subheading": "Heirloom Quality Jewelry",
            "bullets": [
                "Intricate traditional craftsmanship",
                "Premium quality materials",
                "Perfect for every occasion"
            ]
        },
        1: {  # Model Wearing
            "prompt_index": 1,
            "image_type_name": APLUS_BANNER_TYPES[1]["name"],
            "heading": "Grace & Glamour\nIn Every Wear",
            "subheading": "Occasions Made Special",
            "bullets": [
                "Wedding ceremonies & celebrations",
                "Daily elegance & confidence",
                "Anniversary & special moments"
            ]
        },
        2: {  # Front & Back
            "prompt_index": 2,
            "image_type_name": APLUS_BANNER_TYPES[2]["name"],
            "heading": "Front & Back\nDesign Detail",
            "subheading": "Exquisite Craftsmanship",
            "bullets": [
                "Stunning front view with intricate details",
                "Beautiful back design for complete beauty"
            ]
        },
        3: {  # Care Tips
            "prompt_index": 3,
            "image_type_name": APLUS_BANNER_TYPES[3]["name"],
            "heading": "Care & Storage Tips",
            "subheading": "Maintain Your Treasure",
            "bullets": [
                "Store in a safe dry place when not in use",
                "Avoid contact with water, perfume & chemicals",
                "Wipe gently with a soft dry cloth",
                "Keep away from direct sunlight & heat"
            ]
        }
    }
    
    text_dict = defaults[banner_type_index]
    text_dict["theme_line"] = theme_dict.get("theme_line", "")
    return text_dict


# ============================================================================
# IMAGE GENERATION HELPERS
# ============================================================================

def create_aplus_generation_prompts(
    theme_dict: Dict[str, Any],
    earring_description: str = "",
    banner_texts: Dict[int, Any] = None
) -> List[str]:
    """
    Create 4 optimized image generation prompts (one for each A+ banner type)
    using the universal theme and pre-generated text.

    Args:
        theme_dict: Theme dictionary from generate_aplus_theme()
        earring_description: Pre-analyzed earring description
        banner_texts: Dict mapping banner index → text_dict from generate_aplus_banner_text()

    Returns:
        List of 4 prompts (one per banner type)
    """
    prompts = []
    for i in range(4):
        text_dict = (banner_texts or {}).get(i)
        prompt = get_aplus_banner_prompt(i, theme_dict, earring_description, text_dict=text_dict)
        prompts.append(prompt)
    return prompts


# ============================================================================
# VALIDATION & FORMATTING
# ============================================================================

def validate_theme_dict(theme_dict: Dict[str, Any]) -> bool:
    """Validate that theme dict has all required keys."""
    required_keys = [
        "earring_style",
        "metal_tone",
        "primary_colors",
        "mood",
        "background_color",
        "typography_color",
        "typography_style",
        "lighting_mood",
        "theme_line"
    ]
    
    for key in required_keys:
        if key not in theme_dict:
            return False
    
    return True


def validate_banner_text(text_dict: Dict[str, Any]) -> bool:
    """Validate that banner text dict has required keys."""
    required_keys = ["prompt_index", "image_type_name", "heading", "subheading", "bullets"]
    
    for key in required_keys:
        if key not in text_dict:
            return False
    
    if not isinstance(text_dict.get("bullets"), list) or len(text_dict["bullets"]) < 2:
        return False

    return True


# ============================================================================
# EARRING SIZE DETECTION FROM SCALE
# ============================================================================

def detect_earring_size_from_scale(image_bytes: bytes) -> dict:
    """
    Uses GPT-4o mini to read the physical rulers in the earring product image
    and return both height and width in centimeters.

    The product images contain a vertical ruler (left) and horizontal ruler
    (bottom) in cm. GPT-4o mini reads both and returns a dict.

    Returns {"length_cm": float, "width_cm": float}.
    Defaults to {"length_cm": 3.0, "width_cm": 2.0} if detection fails.
    """
    try:
        client = OpenAI()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        },
                        {
                            "type": "text",
                            "text": (
                                "This image has a vertical ruler on the left and a horizontal ruler "
                                "on the bottom, both in centimeters. "
                                "1) Measure the total HEIGHT of the earring from the top of the hook/clasp "
                                "to the very bottom using the vertical ruler. "
                                "2) Measure the total WIDTH of the earring at its widest point "
                                "using the horizontal ruler. "
                                'Return ONLY a JSON object like: {"length_cm": 4.5, "width_cm": 2.0} '
                                "No explanation, no other text. "
                                'If no ruler is visible, return {"length_cm": 3.0, "width_cm": 2.0}.'
                            )
                        }
                    ]
                }
            ],
            max_tokens=30,
            temperature=0
        )

        import json as _json
        raw = response.choices[0].message.content.strip()
        size_dict = _json.loads(raw)
        length_cm = float(size_dict.get("length_cm", 3.0))
        width_cm = float(size_dict.get("width_cm", 2.0))
        print(f"[SIZE DETECTION] Earring: {length_cm}cm height × {width_cm}cm width")
        return {"length_cm": length_cm, "width_cm": width_cm}

    except Exception as e:
        print(f"[SIZE DETECTION] Failed: {e}. Defaulting to 3.0 × 2.0 cm.")
        return {"length_cm": 3.0, "width_cm": 2.0}


def get_ear_canvas_proportion(size_cm: float) -> tuple:
    """
    Maps earring height (cm) to canvas proportion and shot description.

    Returns (ear_size_ratio, shot_description) where ear_size_ratio is
    the fraction of canvas height the ear image should occupy.

    Small studs  (< 1.5cm) → 0.68  — tight close-up, ear fills frame
    Medium       (1.5–3cm) → 0.52  — standard ear shot
    Large        (3–5cm)   → 0.38  — wider, face more visible
    Very long    (> 5cm)   → 0.28  — full portrait, earring hangs naturally
    """
    if size_cm < 1.5:
        return 0.68, "extreme close-up portrait, ear fills right side prominently, partial face profile only"
    elif size_cm < 3.0:
        return 0.52, "close portrait, 3/4 face, ear and earring clearly visible"
    elif size_cm < 5.0:
        return 0.38, "standard portrait, full face and neck visible, ear prominent on right"
    else:
        return 0.28, "full portrait with neck and shoulder, face fully visible, long earring hangs naturally"


# ============================================================================
# MODEL WEARING — TWO-STEP OUTPAINTING
# ============================================================================

def generate_model_wearing_banner(
    image_bytes: bytes,
    theme_dict: Dict[str, Any],
    earring_description: str = "",
    text_dict: Dict[str, Any] = None
) -> Optional[bytes]:
    """
    Two-step outpainting to get a full face model with the EXACT earring:

    Step 1 — Generate ear close-up:
        Uses the proven type5 prompt (tight ear close-up) which reliably
        replicates the exact earring. Result: 1024x1024 ear + earring.

    Step 2 — Outpaint face + banner around the ear:
        Places the ear close-up (scaled down to natural portrait proportion)
        on the RIGHT side of a transparent 1536x1024 canvas.
        Transparent left area = AI generates face, neck, hair connecting
        naturally to the ear.
        Right text area = AI generates heading, bullets, themed background.

    Returns raw PNG bytes of the full 1536x1024 banner, or None on failure.
    """
    from prompts2 import model_wearing_prompt
    from aplus_prompts import format_theme_for_prompt

    client = OpenAI()

    try:
        # ── Step 1: Ear close-up with exact earring ──────────────────────────
        print("[MODEL WEARING] Step 1: Generating ear close-up...")

        # Detect earring size first — large earrings need portrait frame
        size_info = detect_earring_size_from_scale(image_bytes)
        size_cm = size_info["length_cm"]
        ear_ratio, shot_description = get_ear_canvas_proportion(size_cm)
        # Use portrait frame for earrings > 4cm so full dangling length is visible
        step1_size = "1024x1536" if size_cm >= 4.0 else "1024x1024"
        print(f"[MODEL WEARING] Size: {size_cm}cm → step1 size: {step1_size}, ratio: {ear_ratio}")

        ear_prompt = model_wearing_prompt
        if earring_description:
            ear_prompt = f"JEWELRY REFERENCE: {earring_description}\n\n{ear_prompt}"

        img_buffer = io.BytesIO(image_bytes)
        ear_response = client.images.edit(
            model="gpt-image-1.5",
            image=("image.png", img_buffer, "image/png"),
            prompt=ear_prompt,
            size=step1_size,
            quality="low",
            n=1
        )
        ear_bytes = base64.b64decode(ear_response.data[0].b64_json)
        ear_image = Image.open(io.BytesIO(ear_bytes)).convert("RGBA")
        print("[MODEL WEARING] Step 1 complete — ear close-up generated.")

        # ── Step 2: Place ear on canvas, outpaint face + banner ──────────────
        print("[MODEL WEARING] Step 2: Outpainting face around ear...")

        canvas_w, canvas_h = 1536, 1024

        # Scale ear to target height maintaining aspect ratio (not forced square)
        ear_target_h = int(canvas_h * ear_ratio)
        ear_img_w, ear_img_h = ear_image.size
        ear_target_w = int(ear_img_w * ear_target_h / ear_img_h)
        ear_resized = ear_image.resize((ear_target_w, ear_target_h), Image.Resampling.LANCZOS)

        # Place ear on the RIGHT side, vertically centered
        margin_right = int(canvas_w * 0.04)
        ear_x = canvas_w - ear_target_w - margin_right
        ear_y = (canvas_h - ear_target_h) // 2

        # Transparent canvas — transparent areas = AI generates here
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.paste(ear_resized, (ear_x, ear_y), ear_resized)
        print(f"[MODEL WEARING] Canvas: {canvas_w}x{canvas_h}, ear placed at ({ear_x},{ear_y}) size {ear_target_w}x{ear_target_h}")

        canvas_buffer = io.BytesIO()
        canvas.save(canvas_buffer, format="PNG")
        canvas_png_bytes = canvas_buffer.getvalue()

        # Build outpaint prompt
        theme_fmt = format_theme_for_prompt(theme_dict)
        bg_color = theme_fmt["background_color"]
        border = theme_fmt["border_style_description"]
        typography = f"{theme_fmt['typography_color']} {theme_fmt['typography_style']}"
        lighting = theme_fmt["lighting_mood"]
        mood = theme_dict.get("mood", "elegant")

        # Build exact text block for right side
        from aplus_prompts import format_text_block
        text_block = format_text_block(text_dict) if text_dict else (
            "\nHeading (2 lines): occasion-appropriate for this earring style\n"
            "Tagline: when/how to wear these earrings\n"
            "Bullets: 3 styling occasions and tips\n"
        )

        outpaint_prompt = f"""Complete this A+ banner image (1536x1024 landscape).
The earring on a woman's ear is already placed on the RIGHT side — DO NOT change or redraw it.

SHOT FRAMING: {shot_description}

LEFT HALF (50%) — GENERATE:
- Beautiful young Indian woman, age 25-30
- Shot framing: {shot_description}
- Her right ear (shown on right side) connects naturally to her face and neck
- Hair pulled back or swept to keep ear fully visible
- Outfit matches {mood} aesthetic
- Background: exactly {bg_color}
- Lighting: {lighting}, warm natural Indian skin tone
- No earrings on her left ear — only the one already shown on right

RIGHT HALF (50%) — GENERATE:
- Background: exactly {bg_color}
- Typography: {typography}
- Small elegant ornamental divider (NOT a full-width border frame)
{text_block}

FULL IMAGE:
- Seamless {bg_color} background across both halves
- Professional editorial fashion photography quality
- NO watermarks, logos, extra text, or "Shop Now"
- SAFE ZONE: Keep ALL content (face, earring, text) at least 40px inside all 4 edges — outer 40px must be background color only
"""

        outpaint_response = client.images.edit(
            model="gpt-image-1.5",
            image=("image.png", io.BytesIO(canvas_png_bytes), "image/png"),
            prompt=outpaint_prompt,
            size="1536x1024",
            quality="low",
            n=1
        )

        result_bytes = base64.b64decode(outpaint_response.data[0].b64_json)
        print("[MODEL WEARING] Step 2 complete — full banner generated.")
        return result_bytes

    except Exception as e:
        print(f"[MODEL WEARING] Outpainting failed: {e}. Will fall back to standard generation.")
        return None
