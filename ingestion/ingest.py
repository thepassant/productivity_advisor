
import pandas as pd

import minsearch



def load_index(data_path="../data/cleaned_data.csv"):
    df = pd.read_csv(data_path)

    documents = df.to_dict(orient="records")

    index = minsearch.Index(['task', 'category', 'difficulty', 'duration_estimate'
       'framework_name', 'reasoning', 'instructions', 'tags'],
        keyword_fields=["id"],
    )

    index.fit(documents)
    return index