from typing import Dict


STANDARD_SECTIONS = [
    "Headline",
    "Marketing Copy",
    "Call To Action",
    "Platform-Specific Extras",
]

CAMPAIGN_SECTIONS = [
    "Campaign Name",
    "Campaign Goal",
    "Core Message",
    "Platform Content",
    "Call To Action",
]


def is_valid_output(text: str) -> bool:
    """Check whether the AI output has the required structure."""

    if not text:
        return False

    lower_text = text.lower()

    has_standard_sections = all(
        section.lower() in lower_text for section in STANDARD_SECTIONS
    )

    has_campaign_sections = all(
        section.lower() in lower_text for section in CAMPAIGN_SECTIONS
    )

    long_enough = len(text.strip()) > 80

    return long_enough and (has_standard_sections or has_campaign_sections)


def quality_check(text: str, platform: str) -> Dict[str, str]:
    """Simple rule-based quality check for generated content."""

    word_count = len(text.split())
    char_count = len(text)
    lower_text = text.lower()

    cta_words = [
        "buy",
        "try",
        "start",
        "join",
        "discover",
        "shop",
        "learn more",
        "get",
        "visit",
        "explore",
        "download",
        "sign up",
        "book",
        "claim",
    ]

    checks = {
        "Platform": platform,
        "Word Count": str(word_count),
        "Character Count": str(char_count),
        "CTA Detected": "Yes" if any(word in lower_text for word in cta_words) else "No",
        "Complete Structure": "Yes" if is_valid_output(text) else "No",
    }

    if platform == "Campaign":
        checks["Campaign Name Detected"] = "Yes" if "campaign name" in lower_text else "No"
        checks["Core Message Detected"] = "Yes" if "core message" in lower_text else "No"

    if platform in ["Instagram", "LinkedIn"]:
        checks["Hashtags Detected"] = "Yes" if "#" in text else "No"

    if platform == "LinkedIn":
        checks["No Link In Bio"] = "Yes" if "link in bio" not in lower_text else "No"

    if platform == "Email":
        checks["Email Subject Detected"] = "Yes" if "subject" in lower_text else "No"
        checks["Preview Text Detected"] = "Yes" if "preview" in lower_text else "No"

    if platform == "X/Twitter":
        checks["Under 280 Characters"] = "Yes" if char_count <= 280 else "No"

    return checks