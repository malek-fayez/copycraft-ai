import time
from typing import List, Tuple, Callable, Optional

import pandas as pd

from config import REQUIRED_BATCH_COLUMNS
from generator import generate_copy
from prompt_templates import build_generation_prompt


def validate_batch_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    missing_columns = [
        column
        for column in REQUIRED_BATCH_COLUMNS
        if column not in df.columns
    ]

    return len(missing_columns) == 0, missing_columns


def process_batch_copy(
    df: pd.DataFrame,
    temperature: float,
    top_p: float,
    delay: int = 8,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> pd.DataFrame:
    batch_results = []
    total_rows = len(df)

    for position, (_, row) in enumerate(df.iterrows(), start=1):
        product_name = str(row["product_name"])

        if progress_callback:
            progress_callback(position, total_rows, product_name)

        prompt = build_generation_prompt(
            product_name=str(row["product_name"]),
            description=str(row["description"]),
            platform=str(row["platform"]),
            tone=str(row["tone"]),
            audience=str(row["audience"]),
            length=str(row["length"]),
            variation_number=1,
        )

        output = generate_copy(
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
        )

        batch_results.append(
            {
                "product_name": row["product_name"],
                "description": row["description"],
                "audience": row["audience"],
                "platform": row["platform"],
                "tone": row["tone"],
                "length": row["length"],
                "generated_copy": output,
            }
        )

        if position < total_rows and delay > 0:
            time.sleep(delay)

    return pd.DataFrame(batch_results)