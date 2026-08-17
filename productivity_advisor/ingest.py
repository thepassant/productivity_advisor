import pandas as pd
import minsearch


INDEX_FIELDS = [
    "task",
    "category",
    "difficulty",
    "duration_estimate",
    "framework_name",
    "reasoning",
    "instructions",
    "tags",
]


def load_index(data_path="data/cleaned_data.csv"):
    df = pd.read_csv(data_path)

    # Make sure all fields used by MinSearch
    # contain strings.
    for field in INDEX_FIELDS:
        df[field] = (
            df[field]
            .fillna("")
            .astype(str)
        )

    documents = df.to_dict(orient="records")

    index = minsearch.Index(
        INDEX_FIELDS,
        keyword_fields=["id"],
    )

    index.fit(documents)

    return index