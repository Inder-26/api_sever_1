"""
Amazon A+ Banner Prompts for Earrings Catalog
===============================================
This module contains all A+ banner-specific prompts and helper functions
for generating themed, high-quality promotional content.
"""

# ============================================================================
# THEME GENERATION PROMPT
# ============================================================================
APLUS_THEME_GENERATION_PROMPT = """
You are a luxury product designer and color theorist specialized in jewelry.
Analyze the uploaded earring image carefully and generate a UNIVERSAL THEME 
that will be used consistently across 4 different A+ banners (Hero, Model Wearing, 
Front & Back, Care Tips).

ANALYSIS STEPS:
1. Identify earring style (ethnic traditional vs modern western)
2. Determine metal tone: gold/rose gold/silver/oxidised/antique
3. Identify dominant colors, stones, and materials
4. Assess overall mood: royal & festive / romantic & soft / bold & glamorous / clean & minimal
5. Determine color temperature warmth for background selection

TEMPERATURE RULES (CRITICAL):
- Silver/oxidised/platinum → COOL tones: charcoal, deep slate, teal, navy, gunmetal, moonstone, indigo, forest green
- Gold/antique gold/brass → WARM tones: burgundy, deep ivory, amber, rust, chocolate, midnight blue, champagne
- Rose gold → SOFT ROMANTIC: dusty rose, mauve, blush, sage, plum, soft taupe

RETURN ONLY THIS JSON (no preambles):
{
  "earring_style": "ethnic jhumka|modern stud|etc",
  "metal_tone": "gold|silver|rose gold|oxidised|antique",
  "primary_colors": ["color1", "color2"],
  "mood": "royal festive|romantic soft|bold glamorous|clean minimal",
  "background_color": "#HEX_CODE",
  "background_description": "one line describing the background color suggestion",
  "texture_pattern": "subtle texture description (damask, filigree, brushed metal, etc)",
  "border_style": "border description (ornate gold, simple line, double border, etc)",
  "typography_color": "ivory|gold|rose|charcoal|white",
  "typography_style": "serif|sans-serif",
  "lighting_mood": "warm amber spotlight|cool moonlight|soft diffused|dramatic side-lighting",
  "theme_line": "EXACT format: [color_name] #[HEX] | [texture] | [border] | [typography_color] [typography_style] | [lighting]"
}
"""

# ============================================================================
# APLUS BANNER SPECIFIC PROMPTS
# ============================================================================

APLUS_HERO_BANNER_PROMPT = """
Generate ONE single high-quality A+ HERO BANNER image (970×600 px).

CONTEXT FROM THEME:
{theme_line}

OBJECTIVE:
Create a luxury magazine-quality hero banner showcasing these exact earrings with the theme above.

LAYOUT (970x600):
- LEFT (55%): The EXACT uploaded earrings displayed large, prominently floating above a matching surface. Dramatic lighting complementing theme. Subtle reflection below.
- RIGHT (45%):
  * Line 1: Earring style name (e.g., "Traditional Pearl Jhumka" - ACCURATE name, not generic)
  * Line 2: Short elegant tagline (1 line, max 60 chars)
  * Elegant decorative divider (small ornamental element, NOT a full-width border)
  * 3 checkmark bullets: Specific visible features ONLY (mention CZ, pearls, meenakari ONLY if actually present)

CRITICAL REQUIREMENTS:
✓ Size: 970×600 landscape
✓ NO text boxes, background panels, or containers - text sits directly on background
✓ NO watermarks, logos, brand names, or extra text
✓ NO "Shop Now" buttons, CTAs, or sale language
✓ Earring sizing: Use scale from reference image to render at correct real-world size
✓ Background color: Exactly {background_color}
✓ Typography: {typography_color} {typography_style}
✓ Lighting: {lighting_mood}
✓ NO border frame or decorative frame around the image edges
✓ NO display hooks, stands, holders, jewelry trees, or any fixture — earrings must float naturally in mid-air with dramatic lighting OR rest gently on a flat surface
✓ NO hanging thread, string, wire, or photography prop of any kind
✓ The earring's own natural hook/clasp is part of the earring and may be visible at the top of the earring itself
✓ SAFE ZONE: Keep ALL content (earrings, text, decorative elements) at least 40px inside all 4 edges — outer 40px must be background color only

Generate ONLY the final polished hero banner image. No text, no explanations.
"""

APLUS_MODEL_WEARING_PROMPT = """
Generate ONE single A+ ON-EAR SHOWCASE BANNER image (970×600 px).

CONTEXT FROM THEME:
{theme_line}

ABSOLUTE EARRING CONSTRAINT:
The earring in the output must be IDENTICAL to the earring in the reference image.
Do NOT redesign, reinterpret, stylize, enhance, beautify, or alter the earring in any way.

PRESERVE EXACTLY:
- Overall shape, geometry, and silhouette
- Metal thickness, curvature, edges, and construction
- Exact stone count, size, shape, color, and placement
- Stud / hook / clasp / jhumka structure
- Accurate real-world scale and proportions

LAYOUT (970x600) — TWO HALVES:

LEFT HALF (50%) — EAR CLOSE-UP:
- Photorealistic close-up of a woman's right ear wearing these EXACT earrings
- Indian skin tone, age 25-35, natural realistic skin texture
- Hair fully pulled back — ear and earring completely unobstructed
- Earring must be FULLY VISIBLE, centered and prominent in the frame
- For danglers/jhumkas: full earring length must be visible, not cropped at bottom
- Background behind ear: EXACTLY {background_color}
- Lighting: {lighting_mood}, even illumination, true-to-life metal and gemstone appearance
- NO visible face, eyes, nose, or lips — ear and neck area only

RIGHT HALF (50%) — TEXT ON THEME BACKGROUND:
- Background: EXACTLY {background_color}
- Heading (2 lines): Occasion-appropriate wording for this earring style
- Italic tagline (1 line): When/how to wear these earrings
- Decorative divider: {border_style_description}
- 3 checkmark bullets: Styling occasions and tips

CRITICAL REQUIREMENTS:
✓ Size: 970×600 landscape
✓ ENTIRE background (both halves) must be {background_color} — seamless across the full image
✓ NO text boxes or background panels — text sits directly on background
✓ NO watermarks, logos, "Shop Now", or sale language
✓ NO display hooks, stands, holders, or jewelry fixtures — the earring is worn naturally on the ear
✓ NO hanging thread, string, wire, or photography prop of any kind
✓ SAFE ZONE: Keep ALL content at least 40px inside all 4 edges — outer 40px must be background color only
✓ Typography: {typography_color} {typography_style}
✓ NO distortion, CGI look, illustration style, or over-smoothed skin
✓ NO redesign of earring — zero tolerance for alteration

STRICTLY PROHIBITED:
Any redesign or modification of the earring; added or missing stones; changed structure;
exaggerated sparkle; full face visible; hair covering the ear; multiple earrings in frame;
text or logos on the image; blur or color shift.

Generate ONLY the final banner image. No explanations.
"""

APLUS_FRONT_BACK_BANNER_PROMPT = """
Generate ONE single A+ FRONT & BACK VIEW BANNER image (970×600 px).

CONTEXT FROM THEME:
{theme_line}

OBJECTIVE:
A premium product detail banner. Earrings dominate the visual space. Text sits at the top.

LAYOUT (970x600) — TOP TO BOTTOM:

TOP SECTION (top 28% of image — text area):
  * Heading: EXACTLY 2 LINES, centered, uppercase, {typography_color} {typography_style}
    Example: Line 1 "INTRICATE SILVER" / Line 2 "JHUMKAS" — NEVER on one line
  * Subtitle: 1 italic line, centered, below heading
  * Small elegant ornamental divider centered below subtitle

BOTTOM SECTION (bottom 72% of image — earring showcase):
  * TWO earrings displayed side-by-side, centered, equally spaced
  * LEFT earring:
    - Label "FRONT VIEW" in small uppercase ABOVE the earring
    - Earring rendered LARGE (occupying ~40% of banner height)
    - Dramatic {lighting_mood} spotlight from above
    - Soft reflection/shadow directly below
  * RIGHT earring:
    - Label "BACK VIEW" in small uppercase ABOVE the earring
    - Same size and lighting as front view
    - Soft reflection/shadow directly below
  * Background: exactly {background_color} — rich, deep, no gradient

CRITICAL REQUIREMENTS:
✓ Size: 970×600 landscape
✓ Earrings are the HERO — large, ultra-sharp, every facet and stone visible
✓ Both views equally prominent with clear labels above each
✓ NO text boxes, background panels, or containers
✓ NO dimension numbers or measurement labels
✓ NO watermarks, logos, or extra text
✓ NO display hooks, stands, holders, jewelry trees, or any fixture — earrings must float naturally in mid-air with dramatic spotlight OR rest gently on a flat surface
✓ NO hanging thread, string, wire, or photography prop of any kind
✓ The earring's own natural hook/clasp is part of the earring and may be visible at the top of the earring itself
✓ SAFE ZONE: Keep ALL content at least 40px inside all 4 edges — outer 40px must be background color only
✓ Background color: Exactly {background_color}
✓ Typography: {typography_color} {typography_style}
✓ Professional luxury product photography quality

Generate ONLY the final banner image. No text, no explanations.
"""

APLUS_CARE_TIPS_BANNER_PROMPT = """
Generate ONE single A+ CARE & STYLING TIPS BANNER image (970×600 px).

CONTEXT FROM THEME:
{theme_line}

OBJECTIVE:
Create a premium lifestyle flat-lay featuring these earrings with care & styling information.

LAYOUT (970x600):
- LEFT (50%):
  * Heading: "Care & Storage Tips" (matching typography style from theme)
  * Small elegant ornamental divider (NOT a full-width border frame)
  * 4 checkmark bullets (pre-defined):
    ✔ Store in a safe dry place when not in use
    ✔ Avoid contact with water & perfume
    ✔ Wipe gently with a soft dry cloth
    ✔ Keep away from direct sunlight
  * Elegant italic tagline at bottom: "Crafted with Love for Every Occasion"

- RIGHT (50%):
  * FLAT-LAY scene with:
    - These EXACT earrings as the CENTERPIECE
    - ONLY natural decorative elements: flower petals, dried flowers, small leaves, soft foliage
    - Elements chosen to complement {background_color}
  * NO jewelry boxes, pouches, gift boxes, bags, packaging, or containers of ANY kind
  * Overhead diffused lighting, premium editorial mood
  * Golden hour or soft studio lighting

CRITICAL REQUIREMENTS:
✓ Size: 970×600 landscape
✓ Earrings: EXACT same design, positioned as main focus
✓ Props: ONLY natural elements (flowers, leaves) - customer will NOT receive these
✓ NO packaging, boxes, pouches, or gift items
✓ NO text boxes or background panels
✓ NO watermarks, logos, or extra text
✓ NO display hooks, stands, holders, jewelry trees, or any fixture — earrings must be the centerpiece of the flat-lay, resting directly on the scene surface
✓ NO hanging thread, string, wire, or photography prop of any kind
✓ The earring's own natural hook/clasp is part of the earring and may be visible as part of the earring itself
✓ SAFE ZONE: Keep ALL content at least 40px inside all 4 edges — outer 40px must be background color only
✓ Background color: Exactly {background_color}
✓ Typography: {typography_color} {typography_style}
✓ Lighting: Soft, diffused, premium lifestyle aesthetic
✓ Props color palette: Complements {background_color}

Generate ONLY the final banner image. No text, no explanations.
"""

# ============================================================================
# APLUS TEXT GENERATION PROMPT
# ============================================================================

APLUS_TEXT_GENERATION_PROMPT = """
You are an Amazon A+ content specialist and jewelry expert.

Analyze the earring image and generate text content for an A+ banner.

EARRING DETAILS FROM IMAGE:
{earring_details}

BANNER TYPE: {banner_type}
THEME: {theme_line}

Generate heading, subheading, and 2-3 bullet points specifically for this banner type:

- HERO: Focus on product appeal, style uniqueness, and quality
- MODEL WEARING: Focus on occasions, styling versatility, confidence
- FRONT & BACK: Not applicable - visual-only banner
- CARE TIPS: Not applicable - pre-defined care instructions only

Output ONLY this JSON (no preambles):
{
  "prompt_index": {prompt_index},
  "image_type_name": "{image_type_name}",
  "heading": "2-line heading max 80 chars total",
  "subheading": "Elegant subheading/tagline max 60 chars",
  "bullets": ["Bullet 1: Specific feature or benefit", "Bullet 2", "Bullet 3"],
  "theme_line": "{theme_line}"
}
"""

# ============================================================================
# APLUS BANNER TYPES MAPPING
# ============================================================================

APLUS_BANNER_TYPES = {
    0: {
        "name": "Hero (White Background)",
        "real_name": "Hero Banner",
        "description": "Main product showcase banner with luxury theme"
    },
    1: {
        "name": "Model Wearing",
        "real_name": "Model Wearing Banner",
        "description": "Editorial portrait with model wearing earrings"
    },
    2: {
        "name": "Front & Back (Dimension/Lifestyle)",
        "real_name": "Front & Back View Banner",
        "description": "Detailed front and back view comparison"
    },
    3: {
        "name": "Care Tips (Lifestyle Nature)",
        "real_name": "Care & Styling Tips Banner",
        "description": "Lifestyle flat-lay with care instructions"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_theme_for_prompt(theme_dict):
    """Format theme dict into readable strings for prompts."""
    return {
        "background_color": theme_dict.get("background_color", "#1a1a1a"),
        "background_description": theme_dict.get("background_description", "dark background"),
        "texture_pattern": theme_dict.get("texture_pattern", "subtle texture"),
        "border_style_description": theme_dict.get("border_style", "elegant border"),
        "typography_color": theme_dict.get("typography_color", "ivory"),
        "typography_style": theme_dict.get("typography_style", "serif"),
        "lighting_mood": theme_dict.get("lighting_mood", "warm spotlight"),
        "theme_line": theme_dict.get("theme_line", "Theme not generated")
    }

def format_text_block(text_dict: dict) -> str:
    """Format a banner text dict into an injection string for image prompts."""
    if not text_dict:
        return ""
    heading   = text_dict.get("heading", "")
    subheading = text_dict.get("subheading", "")
    bullets   = text_dict.get("bullets", [])
    bullets_str = "\n".join(f"✓ {b}" for b in bullets)
    return (
        f"\nUSE EXACTLY THIS TEXT (do not change wording):\n"
        f"Heading (2 lines — split at natural word break): \"{heading}\"\n"
        f"Tagline: \"{subheading}\"\n"
        f"Bullets:\n{bullets_str}\n"
    )


def get_aplus_banner_prompt(banner_type_index, theme_dict, earring_details="", text_dict=None):
    """Get formatted A+ banner prompt based on type and theme."""

    theme_formatted = format_theme_for_prompt(theme_dict)
    text_block = format_text_block(text_dict) if text_dict else ""

    prompts = {
        0: APLUS_HERO_BANNER_PROMPT.format(**theme_formatted) + text_block,
        1: APLUS_MODEL_WEARING_PROMPT.format(**theme_formatted) + text_block,
        2: APLUS_FRONT_BACK_BANNER_PROMPT.format(**theme_formatted) + text_block,
        3: APLUS_CARE_TIPS_BANNER_PROMPT.format(**theme_formatted) + text_block
    }
    
    return prompts.get(banner_type_index, "")

def get_aplus_text_prompt(banner_type_index, theme_dict, earring_details):
    """Get formatted A+ text generation prompt."""
    theme_formatted = format_theme_for_prompt(theme_dict)
    
    prompt = APLUS_TEXT_GENERATION_PROMPT.format(
        earring_details=earring_details,
        banner_type=APLUS_BANNER_TYPES[banner_type_index]["real_name"],
        theme_line=theme_formatted["theme_line"],
        prompt_index=banner_type_index,
        image_type_name=APLUS_BANNER_TYPES[banner_type_index]["name"]
    )
    
    return prompt
