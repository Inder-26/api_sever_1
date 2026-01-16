
# COMMON STYLE TOKENS (Implied in text)
# Lighting: "Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic."
# Atmosphere: "Clean, crisp, minimalistic, luxury e-commerce presentation."

white_bgd_prompt = """
You are provided with an Earrings image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of elegant earrings (both left and right fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Pure white (#ffffff), seamless studio backdrop.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Clean, crisp, minimalistic, luxury e-commerce presentation.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_1_prompt = """
You are provided with an Earrings image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of elegant earrings (both left and right fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Soft pastel gradient (pastel pink, lavender, ivory, or marble texture) tailored to the earrings' natural hues.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, gentle, Instagram-worthy, sophisticated.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_2_prompt = """
You are provided with an Earrings image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of elegant earrings (both left and right fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Rich textured background (muted teal, matte beige, velvet black, or soft gold) providing elegant contrast.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Premium, editorial, artistic, moody luxury.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

props_img_prompt = """
You are provided with an Earrings image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic flat lay image of elegant earrings (both left and right fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Satin fabric, soft velvet, marble, or handmade paper surface with minimal elegant props (dried flowers, soft petals, small stones, fabric folds). Do not add too many props.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, Instagram-worthy, sophisticated, aesthetic.

Strictly avoid: Overpowering props, busy composition, blurry textures, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

hand_prompt = """
You are provided with an Earrings image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of elegant earrings (both left and right fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Neutral beige or ivory tone. The earrings should rest naturally on an open, well-manicured human hand with the palm facing upward.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing both jewelry and realistic skin textures, subtle natural shadows.

Surface Details: Realistic metal reflections, accurate gemstone clarity, natural skin pores subtly visible.

Overall Atmosphere: Warm, organic, luxurious, and natural feel.

Strictly avoid: Unrealistic or stiff hand poses, over-edited skin, harsh or artificial lighting, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

# ----------------- BRACELETS -----------------

white_bgd_bracelet_prompt = """
You are provided with a Bracelet image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant bracelet (fully visible and centered), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Pure white (#ffffff), seamless studio backdrop.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Clean, crisp, minimalistic, luxury e-commerce presentation.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_1_bracelet_prompt = """
You are provided with a Bracelet image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant bracelet (fully visible and centered), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Soft pastel gradient (pastel pink, lavender, ivory, or marble texture) tailored to the bracelet's natural hues.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, gentle, Instagram-worthy, sophisticated.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_2_bracelet_prompt = """
You are provided with a Bracelet image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant bracelet (fully visible and centered), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Rich textured background (muted teal, matte beige, velvet black, or soft gold) providing elegant contrast.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Premium, editorial, artistic, moody luxury.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

props_img_bracelet_prompt = """
You are provided with a Bracelet image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic flat lay image of an elegant bracelet (fully visible), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Satin fabric, soft velvet, marble, or handmade paper surface with minimal elegant props (dried flowers, soft petals, small stones, fabric folds). Do not add too many props.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, Instagram-worthy, sophisticated, aesthetic.

Strictly avoid: Overpowering props, busy composition, blurry textures, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

hand_bracelet_prompt = """
You are provided with a Bracelet image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant bracelet, precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Neutral beige or ivory tone. The bracelet should be draped naturally around a well-manicured wrist on an open hand.

Lighting & Style: Professional soft studio lighting, sharp focus highlighting both jewelry and realistic skin textures, subtle natural shadows.

Surface Details: Realistic metal reflections, accurate gemstone clarity, natural skin pores subtly visible.

Overall Atmosphere: Warm, organic, luxurious, and natural feel.

Strictly avoid: Unrealistic or stiff hand poses, over-edited skin, harsh or artificial lighting, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

# ----------------- NECKLACES -----------------

white_bgd_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant necklace (fully visible, including clasp and chain), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Pure white (#ffffff), seamless studio backdrop.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Clean, crisp, minimalistic, luxury e-commerce presentation.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_1_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant necklace (fully visible, including clasp and chain), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Soft pastel gradient (pastel pink, lavender, ivory, or marble texture) tailored to the necklace's natural hues.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, gentle, Instagram-worthy, sophisticated.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

multicolor_2_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant necklace (fully visible, including clasp and chain), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Rich textured background (muted teal, matte beige, velvet black, or soft gold) providing elegant contrast.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Premium, editorial, artistic, moody luxury.

Strictly avoid: Blurry textures, cartoon-like rendering, unrealistic reflections, overexposure, or added graphic elements.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

props_img_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic flat lay image of an elegant necklace (fully visible, including clasp and chain), precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Satin fabric, soft velvet, marble, or handmade paper surface with minimal elegant props (dried flowers, soft petals, small stones, fabric folds). Do not add too many props.

Lighting & Style: Professional soft studio lighting, sharp focus emphasizing jewelry details, subtle natural shadows, polished and premium aesthetic.

Surface Details: Realistic metal reflections, accurate gemstone clarity, no distortions or artifacts.

Overall Atmosphere: Luxurious, Instagram-worthy, sophisticated, aesthetic.

Strictly avoid: Overpowering props, busy composition, blurry textures, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

hand_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant necklace, precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Neutral beige or ivory tone. The necklace should rest naturally draped over an open hand.

Lighting & Style: Professional soft studio lighting, sharp focus highlighting both jewelry and realistic skin textures, subtle natural shadows.

Surface Details: Realistic metal reflections, accurate gemstone clarity, natural skin pores subtly visible.

Overall Atmosphere: Warm, organic, luxurious, and natural feel.

Strictly avoid: Unrealistic or stiff poses, over-edited skin, harsh or artificial lighting, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""

neck_necklace_prompt = """
You are provided with a Necklace image. Use this to extract the jewelry design—the design MUST be preserved 100% with no changes.

Create a high-resolution, hyper-realistic image of an elegant necklace, precisely based on the provided reference image.

Preserve exactly: Design details, colors, textures, and proportions.

Background: Neutral beige or ivory tone. The necklace should rest naturally around a well-manicured neck.

Lighting & Style: Professional soft studio lighting, sharp focus highlighting both jewelry and realistic skin textures, subtle natural shadows.

Surface Details: Realistic metal reflections, accurate gemstone clarity, natural skin pores subtly visible.

Overall Atmosphere: Warm, organic, luxurious, and natural feel.

Strictly avoid: Unrealistic or stiff poses, over-edited skin, harsh or artificial lighting, cartoon-like rendering.

Output: Generate only the final polished image, without any additional text, captions, or descriptions.

Negative Prompt: IMPORTANT: The design must be preserved 100%. Do not hallucinate new details. Do not change the design.
"""