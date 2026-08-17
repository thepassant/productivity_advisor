import os

import minsearch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from productivity_advisor.ingest import load_index
from productivity_advisor.openai import client


DATA_PATH = os.getenv(
    "DATA_PATH",
    "data/cleaned_data.csv",
)

index = load_index(DATA_PATH)


# ---------------------------------------------------------
# KEYWORD SEARCH BOOSTS
# ---------------------------------------------------------

BOOST = {
    "task": 2.5,
    "instructions": 1.8,
    "reasoning": 2.2,
    "tags": 1.4,
    "category": 1.1,
    "difficulty": 0.9,
}


# ---------------------------------------------------------
# KEYWORD SEARCH
# ---------------------------------------------------------

def search(query, filters=None, num_results=10):
    if filters is None:
        filters = {}

    return index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=num_results,
    )


# ---------------------------------------------------------
# HYBRID SEARCH
# ---------------------------------------------------------
EMBEDDING_MODEL = "text-embedding-3-small"


def embed_texts(texts):
    if isinstance(texts, str):
        texts = [texts]

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [
        item.embedding
        for item in response.data
    ]

def hybrid_search(
    query,
    filters=None,
    k_keyword=50,
    k_final=10,
    w_keyword=0.4,
    w_semantic=0.6,
):
    if filters is None:
        filters = {}

    # -----------------------------------------
    # 1. Keyword retrieval
    # -----------------------------------------

    candidates = index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=k_keyword,
    )

    if not candidates:
        return []

    # -----------------------------------------
    # 2. Keyword scores
    # -----------------------------------------

    keyword_scores = np.array(
        [doc["_score"] for doc in candidates],
        dtype=float,
    )

    # Normalize keyword scores to 0-1
    if keyword_scores.max() > 0:
        keyword_scores = (
            keyword_scores / keyword_scores.max()
        )

    # -----------------------------------------
    # 3. Semantic scores
    # -----------------------------------------

    query_embedding = embed_texts(query)

    document_texts = [
        document_to_text(doc)
        for doc in candidates
    ]   

    document_embeddings = embed_texts(document_texts)

    semantic_scores = cosine_similarity(
        [query_embedding],
        document_embeddings,
    )[0]

    # -----------------------------------------
    # 4. Combine scores
    # -----------------------------------------

    hybrid_scores = (
        w_keyword * keyword_scores
        + w_semantic * semantic_scores
    )

    # -----------------------------------------
    # 5. Rank
    # -----------------------------------------

    ranked_indices = np.argsort(
        -hybrid_scores
    )

    top_docs = [
        candidates[i]
        for i in ranked_indices[:k_final]
    ]

    return top_docs
def document_to_text(doc):
    fields = [
        "task",
        "category",
        "difficulty",
        "duration_estimate",
        "framework_name",
        "reasoning",
        "instructions",
        "tags",
    ]

    return " ".join(
        str(doc.get(field, ""))
        for field in fields
    )

def semantic_search(
    query,
    filters=None,
    k_candidates=50,
    k_final=10,
):
    if filters is None:
        filters = {}

    candidates = index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=k_candidates,
    )

    if not candidates:
        return []

    query_embedding = embed_texts(query)

    document_texts = [
        document_to_text(doc)
        for doc in candidates
    ]

    document_embeddings = embed_texts(
        document_texts
    )

    semantic_scores = cosine_similarity(
        [query_embedding],
        document_embeddings,
    )[0]

    ranked_indices = np.argsort(
        -semantic_scores
    )

    return [
        candidates[i]
        for i in ranked_indices[:k_final]
    ]

def retrieve(
    query,
    method="hybrid",
):
    if method == "keyword":
        return search(
            query,
            num_results=10,
        )

    if method == "semantic":
        return semantic_search(
            query,
            k_final=10,
        )

    if method == "hybrid":
        return hybrid_search(
            query,
            k_final=10,
        )

    raise ValueError(
        f"Unknown retrieval method: {method}"
    )