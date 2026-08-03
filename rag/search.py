from ingestion import ingest
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Load MinSearch index once
index = ingest.load_index()

# Boost dictionary for keyword search
BOOST = {
    "task": 2.5,
    "instructions": 1.8,
    "reasoning": 2.2,
    "tags": 1.4,
    "category": 1.1,
    "difficulty": 0.9,
}


def search(query, filters=None, num_results=10):
    if filters is None:
        filters = {}

    results = index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=num_results,
    )
    return results


# ---------------------------------------------------------
# HYBRID SEARCH
# ---------------------------------------------------------

def hybrid_search(
    query,
    embed_fn=None,
    filters=None,
    k_keyword=50,
    k_final=10,
    w_keyword=0.4,
    w_semantic=0.6,
):
    """
    Hybrid search combining MinSearch keyword scores + semantic scores.

    Parameters:
        query (str): User query.
        embed_fn (callable): Function that returns embeddings. If None → semantic score = 0.
        filters (dict): Optional metadata filters.
        k_keyword (int): Number of keyword candidates to retrieve.
        k_final (int): Number of final results to return.
        w_keyword (float): Weight for keyword score.
        w_semantic (float): Weight for semantic score.

    Returns:
        list: Ranked list of documents.
    """

    if filters is None:
        filters = {}

    # 1. Keyword retrieval
    candidates = index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=k_keyword,
    )

    if not candidates:
        return []

    # Extract keyword scores
    keyword_scores = np.array([doc["_score"] for doc in candidates])

    # 2. Semantic scoring
    if embed_fn is not None:
        query_emb = embed_fn(query)
        doc_texts = [doc["full_text"] for doc in candidates]
        doc_embs = embed_fn(doc_texts)

        semantic_scores = cosine_similarity([query_emb], doc_embs)[0]
    else:
        semantic_scores = np.zeros(len(candidates))

    # 3. Hybrid score
    hybrid_scores = (
        w_keyword * keyword_scores +
        w_semantic * semantic_scores
    )

    # 4. Sort by hybrid score
    top_indices = np.argsort(-hybrid_scores)
    top_docs = [candidates[i] for i in top_indices[:k_final]]

    return top_docs


