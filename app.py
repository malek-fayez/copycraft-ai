import json
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from batch_processor import process_batch_copy, validate_batch_dataframe
from config import (
    APP_SUBTITLE,
    APP_TITLE,
    CAMPAIGN_TYPES,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    LENGTHS,
    PLATFORMS,
    TONES,
)
from generator import generate_copy
from prompt_templates import (
    build_campaign_prompt,
    build_generation_prompt,
    build_tone_transform_prompt,
)
from quality_checker import quality_check


# =========================
# Page Setup
# =========================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="✍️",
    layout="wide",
)

st.title(APP_TITLE)
st.subheader(APP_SUBTITLE)


# =========================
# Session State
# =========================

if "generation_results" not in st.session_state:
    st.session_state.generation_results = []

if "campaign_output" not in st.session_state:
    st.session_state.campaign_output = ""

if "transformed_output" not in st.session_state:
    st.session_state.transformed_output = ""

if "transformed_platform" not in st.session_state:
    st.session_state.transformed_platform = "Instagram"

if "batch_results_df" not in st.session_state:
    st.session_state.batch_results_df = None


# =========================
# Helper Functions
# =========================

def display_quality_checks(checks: Dict[str, str]) -> None:
    for key, value in checks.items():
        st.write(f"**{key}:** {value}")


def brand_profile_inputs(prefix: str):
    with st.expander("Brand Profile Optional"):
        brand_name = st.text_input(
            "Brand Name",
            placeholder="Example: HydroLife",
            key=f"{prefix}_brand_name",
        )

        brand_voice = st.text_input(
            "Brand Voice",
            placeholder="Example: premium, simple, trustworthy",
            key=f"{prefix}_brand_voice",
        )

        unique_selling_point = st.text_area(
            "Unique Selling Point",
            placeholder="Example: Tracks hydration automatically and syncs with a mobile app.",
            height=90,
            key=f"{prefix}_usp",
        )

        forbidden_words = st.text_input(
            "Forbidden Words",
            placeholder="Example: cheap, magic, guaranteed",
            key=f"{prefix}_forbidden_words",
        )

    return brand_name, brand_voice, unique_selling_point, forbidden_words


def display_generation_results(results: List[Dict[str, object]]) -> None:
    if not results:
        return

    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.header("Generated Output")

        for item in results:
            st.subheader(f"Variation {item['variation']}")
            st.markdown(str(item["output"]))
            st.divider()

    with right_col:
        st.header("Quality Check")

        for item in results:
            st.write(f"Variation {item['variation']}")

            checks = quality_check(
                text=str(item["output"]),
                platform=str(item["platform"]),
            )

            display_quality_checks(checks)
            st.divider()

    output_json = json.dumps(results, indent=4)

    st.download_button(
        label="Download Results as JSON",
        data=output_json,
        file_name="copycraft_ai_output.json",
        mime="application/json",
        key="download_generation_json",
    )

    output_txt = "\n\n".join(
        [
            f"Variation {item['variation']}\n\n{item['output']}"
            for item in results
        ]
    )

    st.download_button(
        label="Download Results as TXT",
        data=output_txt,
        file_name="copycraft_ai_output.txt",
        mime="text/plain",
        key="download_generation_txt",
    )


def display_single_output(output: str, platform: str, download_name: str) -> None:
    if not output:
        return

    st.subheader("Generated Output")
    st.markdown(output)

    st.subheader("Quality Check")
    checks = quality_check(output, platform)
    display_quality_checks(checks)

    st.download_button(
        label="Download Output",
        data=output,
        file_name=download_name,
        mime="text/plain",
        key=f"download_{download_name}",
    )


def display_batch_results(result_df: Optional[pd.DataFrame]) -> None:
    if result_df is None or result_df.empty:
        return

    st.subheader("Batch Generation Results")
    st.dataframe(result_df, use_container_width=True)

    csv_output = result_df.to_csv(index=False)

    st.download_button(
        label="Download Batch Results as CSV",
        data=csv_output,
        file_name="batch_copycraft_results.csv",
        mime="text/csv",
        key="download_batch_results",
    )


# =========================
# Tabs
# =========================

copy_tab, campaign_tab, tone_tab, batch_tab = st.tabs(
    [
        "AI Copy Generator",
        "Campaign Builder",
        "Tone Rewriter",
        "Batch Content Pipeline",
    ]
)


# =========================
# AI Copy Generator
# =========================

with copy_tab:
    st.header("AI Copy Generator")
    st.write("Generate platform-specific copy for one product.")

    input_col, parameter_col = st.columns([2, 1])

    with input_col:
        product_name = st.text_input(
            "Product Name",
            placeholder="Example: SmartBottle",
            key="copy_product_name",
        )

        description = st.text_area(
            "Product Description",
            placeholder="Example: A smart water bottle that tracks hydration and reminds users to drink water.",
            height=130,
            key="copy_description",
        )

        audience = st.text_input(
            "Target Audience",
            placeholder="Example: busy professionals and gym users",
            key="copy_audience",
        )

        platform = st.selectbox(
            "Platform",
            PLATFORMS,
            key="copy_platform",
        )

        tone = st.selectbox(
            "Tone",
            TONES,
            key="copy_tone",
        )

        length = st.selectbox(
            "Output Length",
            LENGTHS,
            key="copy_length",
        )

        brand_name, brand_voice, unique_selling_point, forbidden_words = brand_profile_inputs(
            prefix="copy"
        )

    with parameter_col:
        st.subheader("Generation Settings")

        variations = st.radio(
            "Number of Variations",
            [1, 3],
            horizontal=True,
            key="copy_variations",
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            key="copy_temperature",
        )

        top_p = st.slider(
            "Top_P",
            min_value=0.1,
            max_value=1.0,
            value=DEFAULT_TOP_P,
            step=0.05,
            key="copy_top_p",
        )

        generate_button = st.button(
            "Generate Copy",
            type="primary",
            use_container_width=True,
        )

    if generate_button:
        if not product_name or not description or not audience:
            st.warning("Please fill in product name, product description, and target audience.")
        else:
            results = []

            with st.spinner("Generating copy..."):
                for variation_number in range(1, variations + 1):
                    prompt = build_generation_prompt(
                        product_name=product_name,
                        description=description,
                        platform=platform,
                        tone=tone,
                        audience=audience,
                        length=length,
                        variation_number=variation_number,
                        brand_name=brand_name,
                        brand_voice=brand_voice,
                        unique_selling_point=unique_selling_point,
                        forbidden_words=forbidden_words,
                    )

                    output = generate_copy(
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                    )

                    results.append(
                        {
                            "variation": variation_number,
                            "product_name": product_name,
                            "platform": platform,
                            "tone": tone,
                            "temperature": temperature,
                            "top_p": top_p,
                            "output": output,
                        }
                    )

            st.session_state.generation_results = results

    display_generation_results(st.session_state.generation_results)


# =========================
# Campaign Builder
# =========================

with campaign_tab:
    st.header("Campaign Builder")
    st.write("Create a mini marketing campaign across multiple platforms.")

    campaign_input_col, campaign_param_col = st.columns([2, 1])

    with campaign_input_col:
        campaign_product_name = st.text_input(
            "Product Name",
            placeholder="Example: SmartBottle",
            key="campaign_product_name",
        )

        campaign_description = st.text_area(
            "Product Description",
            placeholder="Example: A smart water bottle that tracks hydration and reminds users to drink water.",
            height=130,
            key="campaign_description",
        )

        campaign_audience = st.text_input(
            "Target Audience",
            placeholder="Example: busy professionals and gym users",
            key="campaign_audience",
        )

        campaign_goal = st.text_input(
            "Campaign Goal",
            placeholder="Example: Increase awareness and drive product trials.",
            key="campaign_goal",
        )

        selected_platforms = st.multiselect(
            "Campaign Platforms",
            PLATFORMS,
            default=["Instagram", "LinkedIn", "Email"],
            key="campaign_platforms",
        )

        campaign_type = st.selectbox(
            "Campaign Type",
            CAMPAIGN_TYPES,
            key="campaign_type",
        )

        campaign_tone = st.selectbox(
            "Tone",
            TONES,
            key="campaign_tone",
        )

        campaign_length = st.selectbox(
            "Output Length",
            LENGTHS,
            key="campaign_length",
        )

        (
            campaign_brand_name,
            campaign_brand_voice,
            campaign_unique_selling_point,
            campaign_forbidden_words,
        ) = brand_profile_inputs(prefix="campaign")

    with campaign_param_col:
        st.subheader("Campaign Settings")

        campaign_temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            key="campaign_temperature",
        )

        campaign_top_p = st.slider(
            "Top_P",
            min_value=0.1,
            max_value=1.0,
            value=DEFAULT_TOP_P,
            step=0.05,
            key="campaign_top_p",
        )

        campaign_button = st.button(
            "Build Campaign",
            type="primary",
            use_container_width=True,
        )

    if campaign_button:
        if (
            not campaign_product_name
            or not campaign_description
            or not campaign_audience
            or not campaign_goal
            or not selected_platforms
        ):
            st.warning(
                "Please fill in product name, description, audience, campaign goal, and select at least one platform."
            )
        else:
            campaign_prompt = build_campaign_prompt(
                product_name=campaign_product_name,
                description=campaign_description,
                audience=campaign_audience,
                campaign_type=campaign_type,
                campaign_goal=campaign_goal,
                selected_platforms=selected_platforms,
                tone=campaign_tone,
                length=campaign_length,
                brand_name=campaign_brand_name,
                brand_voice=campaign_brand_voice,
                unique_selling_point=campaign_unique_selling_point,
                forbidden_words=campaign_forbidden_words,
            )

            with st.spinner("Building campaign..."):
                st.session_state.campaign_output = generate_copy(
                    prompt=campaign_prompt,
                    temperature=campaign_temperature,
                    top_p=campaign_top_p,
                )

    display_single_output(
        output=st.session_state.campaign_output,
        platform="Campaign",
        download_name="copycraft_campaign.txt",
    )


# =========================
# Tone Rewriter
# =========================

with tone_tab:
    st.header("Tone Rewriter")
    st.write("Rewrite existing marketing copy into a new tone.")

    tone_col1, tone_col2 = st.columns([2, 1])

    with tone_col1:
        original_copy = st.text_area(
            "Original Marketing Copy",
            placeholder="Paste the copy you want to rewrite...",
            height=220,
            key="tone_original_copy",
        )

    with tone_col2:
        transformer_platform = st.selectbox(
            "Target Platform",
            PLATFORMS,
            key="tone_platform",
        )

        new_tone = st.selectbox(
            "New Tone",
            TONES,
            key="tone_new_tone",
        )

        transformer_temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            key="tone_temperature",
        )

        transformer_top_p = st.slider(
            "Top_P",
            min_value=0.1,
            max_value=1.0,
            value=DEFAULT_TOP_P,
            step=0.05,
            key="tone_top_p",
        )

        transform_button = st.button(
            "Rewrite Tone",
            type="primary",
            use_container_width=True,
        )

    if transform_button:
        if not original_copy:
            st.warning("Please paste marketing copy first.")
        else:
            transform_prompt = build_tone_transform_prompt(
                original_copy=original_copy,
                new_tone=new_tone,
                platform=transformer_platform,
            )

            with st.spinner("Rewriting tone..."):
                st.session_state.transformed_output = generate_copy(
                    prompt=transform_prompt,
                    temperature=transformer_temperature,
                    top_p=transformer_top_p,
                )

            st.session_state.transformed_platform = transformer_platform

    display_single_output(
        output=st.session_state.transformed_output,
        platform=st.session_state.transformed_platform,
        download_name="transformed_copy.txt",
    )


# =========================
# Batch Content Pipeline
# =========================

with batch_tab:
    st.header("Batch Content Pipeline")
    st.write("Upload a CSV file and generate marketing copy for multiple products.")

    sample_csv = """product_name,description,audience,platform,tone,length
SmartBottle,A smart water bottle that tracks hydration and reminds users to drink water,Busy professionals and gym users,Instagram,Friendly,Short
StudyMate,An AI study assistant that helps students summarize lessons and create quizzes,University students,LinkedIn,Professional,Medium
FitSnack,A healthy protein snack designed for gym users and busy people,Gym users and busy professionals,Facebook,Persuasive,Short
"""

    st.download_button(
        label="Download Sample CSV Template",
        data=sample_csv,
        file_name="sample_products.csv",
        mime="text/csv",
        key="download_sample_csv",
    )

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
    )

    batch_col1, batch_col2, batch_col3 = st.columns(3)

    with batch_col1:
        batch_temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            key="batch_temperature",
        )

    with batch_col2:
        batch_top_p = st.slider(
            "Top_P",
            min_value=0.1,
            max_value=1.0,
            value=DEFAULT_TOP_P,
            step=0.05,
            key="batch_top_p",
        )

    with batch_col3:
        batch_delay = st.number_input(
            "Delay Between Requests",
            min_value=0,
            max_value=30,
            value=8,
            step=1,
            help="Use delay to reduce Gemini rate-limit errors.",
        )

    batch_button = st.button(
        "Generate Batch Copy",
        type="primary",
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            st.subheader("Uploaded Data Preview")
            st.dataframe(df, use_container_width=True)

            is_valid, missing_columns = validate_batch_dataframe(df)

            if not is_valid:
                st.error("Missing required columns: " + ", ".join(missing_columns))

            elif df.empty:
                st.error("The uploaded CSV file is empty.")

            elif batch_button:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(position: int, total: int, product: str) -> None:
                    status_text.write(f"Generating copy for {product} ({position}/{total})...")
                    progress_bar.progress(position / total)

                with st.spinner("Generating batch copy..."):
                    result_df = process_batch_copy(
                        df=df,
                        temperature=batch_temperature,
                        top_p=batch_top_p,
                        delay=batch_delay,
                        progress_callback=update_progress,
                    )

                status_text.write("Batch generation completed.")
                st.session_state.batch_results_df = result_df

        except Exception as error:
            st.error(f"Could not read the uploaded CSV file: {error}")

    display_batch_results(st.session_state.batch_results_df)