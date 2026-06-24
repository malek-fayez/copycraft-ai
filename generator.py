import time
from typing import List

from google import genai
from google.genai import types

from config import (
    API_KEY,
    MODEL_NAME,
    MAX_OUTPUT_TOKENS,
    MAX_RETRIES,
)
from quality_checker import is_valid_output


def get_model_candidates() -> List[str]:
    """Return Gemini fallback models without duplicates."""

    candidates = [
        MODEL_NAME,
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    cleaned_candidates = []

    for model in candidates:
        if model and model not in cleaned_candidates:
            cleaned_candidates.append(model)

    return cleaned_candidates


def get_gemini_client():
    """Create Gemini client."""

    if not API_KEY:
        return None

    return genai.Client(api_key=API_KEY)


def is_retryable_error(error_message: str) -> bool:
    """Check if an API error can be retried."""

    retryable_keywords = [
        "429",
        "503",
        "RESOURCE_EXHAUSTED",
        "UNAVAILABLE",
        "Too Many Requests",
        "high demand",
    ]

    return any(keyword in error_message for keyword in retryable_keywords)


def is_model_not_found_error(error_message: str) -> bool:
    """Check if the selected model is unavailable."""

    not_found_keywords = [
        "404",
        "NOT_FOUND",
        "not found",
        "not supported",
    ]

    return any(keyword in error_message for keyword in not_found_keywords)


def format_clean_error(error_message: str) -> str:
    """Convert technical API errors into user-friendly messages."""

    lower_error = error_message.lower()

    if "resource_exhausted" in lower_error or "429" in lower_error:
        return (
            "ERROR: The AI service is currently rate-limited.\n\n"
            "Please wait a few minutes, reduce the batch size, or increase the delay between requests."
        )

    if "unavailable" in lower_error or "503" in lower_error or "high demand" in lower_error:
        return (
            "ERROR: The AI model is temporarily busy.\n\n"
            "Please try again in a few minutes or use fewer variations."
        )

    if "not_found" in lower_error or "404" in lower_error:
        return (
            "ERROR: The selected Gemini model is not available.\n\n"
            "Set GEMINI_MODEL=gemini-2.5-flash in your .env file and restart the app."
        )

    if "api_key" in lower_error or "permission" in lower_error:
        return (
            "ERROR: API authentication failed.\n\n"
            "Check that your GEMINI_API_KEY is correct in the .env file."
        )

    return (
        "ERROR: The AI service could not complete the request.\n\n"
        "Please check your API key, internet connection, and model name."
    )


def generate_copy(
    prompt: str,
    temperature: float,
    top_p: float,
) -> str:
    """Generate AI copy using Gemini with retries and clean error handling."""

    client = get_gemini_client()

    if client is None:
        return (
            "ERROR: Missing Gemini API key.\n\n"
            "Add GEMINI_API_KEY to your .env file and restart the app."
        )

    model_candidates = get_model_candidates()
    last_error = ""

    for model in model_candidates:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=top_p,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                    ),
                )

                output = response.text.strip() if response.text else ""

                if is_valid_output(output):
                    return output

                last_error = (
                    f"Incomplete response from {model}. "
                    f"Attempt {attempt}/{MAX_RETRIES}."
                )

                time.sleep(2)

            except Exception as error:
                error_message = str(error)
                last_error = error_message

                if is_model_not_found_error(error_message):
                    break

                if is_retryable_error(error_message):
                    time.sleep(3 * attempt)
                    continue

                return format_clean_error(error_message)

    return format_clean_error(last_error)