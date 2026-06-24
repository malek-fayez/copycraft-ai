import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

APP_TITLE = "CopyCraft AI"
APP_SUBTITLE = (
    "AI-powered marketing content studio for platform-specific copy generation, "
    "campaign building, tone rewriting, and batch content creation."
)

DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
MAX_OUTPUT_TOKENS = 1400
MAX_RETRIES = 3

PLATFORMS = ["Instagram", "LinkedIn", "Email", "X/Twitter", "Facebook"]

TONES = [
    "Professional",
    "Friendly",
    "Witty",
    "Luxury",
    "Persuasive",
    "Casual",
]

LENGTHS = ["Short", "Medium", "Long"]

CAMPAIGN_TYPES = [
    "Product Launch Campaign",
    "Discount Campaign",
    "Social Media Campaign",
    "Email Campaign",
    "Awareness Campaign",
]

REQUIRED_BATCH_COLUMNS = [
    "product_name",
    "description",
    "audience",
    "platform",
    "tone",
    "length",
]