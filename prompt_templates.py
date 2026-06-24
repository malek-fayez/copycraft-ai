from typing import List


def build_brand_profile_section(
    brand_name: str = "",
    brand_voice: str = "",
    unique_selling_point: str = "",
    forbidden_words: str = "",
) -> str:
    """Build optional brand profile section for prompts."""

    return f"""
Brand Profile:
Brand Name: {brand_name if brand_name else "Not specified"}
Brand Voice: {brand_voice if brand_voice else "Not specified"}
Unique Selling Point: {unique_selling_point if unique_selling_point else "Not specified"}
Forbidden Words or Phrases: {forbidden_words if forbidden_words else "None"}
"""


def build_generation_prompt(
    product_name: str,
    description: str,
    platform: str,
    tone: str,
    audience: str,
    length: str,
    variation_number: int,
    brand_name: str = "",
    brand_voice: str = "",
    unique_selling_point: str = "",
    forbidden_words: str = "",
) -> str:
    """Prompt for single marketing copy generation."""

    brand_profile = build_brand_profile_section(
        brand_name=brand_name,
        brand_voice=brand_voice,
        unique_selling_point=unique_selling_point,
        forbidden_words=forbidden_words,
    )

    return f"""
You are a professional AI marketing copywriter.

Task:
Generate complete marketing copy for the following product.

Product Name:
{product_name}

Product Description:
{description}

Target Platform:
{platform}

Target Audience:
{audience}

Tone:
{tone}

Output Length:
{length}

Variation Number:
{variation_number}

{brand_profile}

Platform Rules:
- Instagram: use a catchy hook, short caption, light emojis, CTA, and hashtags.
- LinkedIn: use a professional business tone, clear value proposition, no casual phrases, and minimal or no emojis.
- Email: include Subject Line, Preview Text, Email Body, and CTA.
- X/Twitter: keep the copy short and character-conscious.
- Facebook: make it friendly, clear, and promotional.

Output Format:
Return the final answer only.
Do not say "Here's your marketing copy".

Use this exact structure:

Headline:
[write one complete headline]

Marketing Copy:
[write the complete marketing copy]

Call To Action:
[write one clear CTA]

Platform-Specific Extras:
[write hashtags, subject line, preview text, or other extras depending on the platform]

Important:
- Complete every section.
- Do not stop after writing the section title.
- Do not leave placeholders.
- Do not invent unrealistic product claims.
- Follow the brand profile if provided.
- Avoid forbidden words or phrases.
- Keep the selected tone consistent.
- Make the output clearly suitable for {platform}.
"""


def build_campaign_prompt(
    product_name: str,
    description: str,
    audience: str,
    campaign_type: str,
    campaign_goal: str,
    selected_platforms: List[str],
    tone: str,
    length: str,
    brand_name: str = "",
    brand_voice: str = "",
    unique_selling_point: str = "",
    forbidden_words: str = "",
) -> str:
    """Prompt for campaign generation."""

    platforms_text = ", ".join(selected_platforms)

    brand_profile = build_brand_profile_section(
        brand_name=brand_name,
        brand_voice=brand_voice,
        unique_selling_point=unique_selling_point,
        forbidden_words=forbidden_words,
    )

    return f"""
You are a senior AI marketing strategist and copywriter.

Task:
Create a complete mini marketing campaign for the product below.

Product Name:
{product_name}

Product Description:
{description}

Target Audience:
{audience}

Campaign Type:
{campaign_type}

Campaign Goal:
{campaign_goal}

Selected Platforms:
{platforms_text}

Tone:
{tone}

Output Length:
{length}

{brand_profile}

Platform Rules:
- Instagram: short, engaging, light emojis, hashtags, strong visual-style caption.
- LinkedIn: professional, business-focused, no "link in bio", minimal emojis.
- Email: include subject line, preview text, body, and CTA.
- X/Twitter: concise and character-conscious.
- Facebook: friendly, clear, and promotional.

Output Format:
Return the final campaign only.
Do not include explanations.

Use this exact structure:

Campaign Name:
[write a clear campaign name]

Campaign Goal:
[write the campaign goal in one sentence]

Core Message:
[write the main message of the campaign]

Platform Content:
[write separate content for each selected platform]

Call To Action:
[write one main CTA for the campaign]

Hashtags:
[write relevant hashtags if suitable]

Notes:
[write short notes about platform adaptation]

Important:
- Do not invent unrealistic claims.
- Follow the brand profile if provided.
- Avoid forbidden words or phrases.
- Make the campaign useful and realistic.
- Adapt the copy clearly for each selected platform.
"""


def build_tone_transform_prompt(
    original_copy: str,
    new_tone: str,
    platform: str,
) -> str:
    """Prompt for tone rewriting."""

    return f"""
You are a professional AI marketing copywriter.

Task:
Rewrite the following marketing copy in a new tone and make it suitable for the selected platform.

Original Copy:
{original_copy}

Target Platform:
{platform}

New Tone:
{new_tone}

Platform Rules:
- Instagram: use a catchy hook, short caption, light emojis, CTA, and hashtags.
- LinkedIn: use a professional business tone, clear value proposition, no casual phrases, and minimal or no emojis.
- Email: include Subject Line, Preview Text, Email Body, and CTA.
- X/Twitter: keep the copy short and character-conscious.
- Facebook: make it friendly, clear, and promotional.

Output Format:
Return the final answer only.
Do not say "Here's the rewritten marketing copy".

Use this exact structure:

Headline:
[rewritten headline]

Marketing Copy:
[rewritten marketing copy]

Call To Action:
[rewritten CTA]

Platform-Specific Extras:
[hashtags, subject line, preview text, or other platform-specific extras]

Important:
- Keep the same product meaning.
- Do not add fake claims.
- Remove platform-inappropriate language.
- If the target platform is LinkedIn, do not use "link in bio".
- If the target platform is LinkedIn, avoid excessive emojis.
- Keep the new tone consistent.
- Complete every section.
"""