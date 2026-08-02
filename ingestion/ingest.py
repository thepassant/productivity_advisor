import os
import pandas as pd

import minsearch


DATA_PATH = os.getenv("DATA_PATH", "../data/cleaned_data.csv")


def load_index(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    documents = df.to_dict(orient="records")

    index = minsearch.Index(['task', 'category', 'difficulty', 'duration_estimate'
       'framework_name', 'reasoning', 'instructions', 'tags'],
        keyword_fields=["id"],
    )

    index.fit(documents)
    return index