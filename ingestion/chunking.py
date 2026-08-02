
def chunk_text(text, max_length=300):
    """
    Splits text into smaller chunks if it exceeds max_length.
    Simple slicing works perfectly for your dataset.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_length
        chunk = text[start:end].strip()
        chunks.append(chunk)
        start = end

    return chunks


def chunk_documents(documents, max_length=300):
    """
    Converts each document into one or more chunks.
    Each chunk keeps the original metadata and gets a unique ID.
    """
    chunked_docs = []

    for doc in documents:
        text_chunks = chunk_text(doc["text"], max_length=max_length)

        for i, chunk in enumerate(text_chunks):
            chunked_docs.append({
                "id": f"{doc['id']}_chunk_{i}",
                "text": chunk,
                "metadata": doc["metadata"]
            })

    return chunked_docs
