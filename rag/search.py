from ingestion import ingest


# Load MinSearch index once at import time
index = ingest.load_index()


# Boost dictionary for ranking fields
BOOST = {
    "task": 2.5,
    "instructions": 1.8,
    "reasoning": 2.2,
    "tags": 1.4,
    "category": 1.1,
    "difficulty": 0.9,
}


def search(query, filters=None, num_results=10):
    """
    Perform a search over the productivity tasks index.

    Parameters:
        query (str): The user query.
        filters (dict): Optional metadata filters, e.g. {"difficulty": "easy"}.
        num_results (int): Number of results to return.

    Returns:
        list: Ranked list of documents.
    """

    if filters is None:
        filters = {}

    results = index.search(
        query=query,
        filter_dict=filters,
        boost_dict=BOOST,
        num_results=num_results,
    )

    return results
