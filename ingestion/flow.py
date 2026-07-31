from prefect import flow, task
import pandas as pd
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# -----------------------------
# CONFIG
# -----------------------------
DATA_PATH = "data/"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# -----------------------------
# TASKS
# -----------------------------

@task
def load_csv_files():
    tasks = pd.read_csv(f"{DATA_PATH}tasks.csv")
    frameworks = pd.read_csv(f"{DATA_PATH}productivity_frameworks.csv")
    mappings = pd.read_csv(f"{DATA_PATH}framework_task_mapping.csv")
    return tasks, frameworks, mappings


@task
def build_documents(tasks, frameworks, mappings):
    docs = []

    # Tasks
    for _, row in tasks.iterrows():
        docs.append({
            "id": f"task_{row['id']}",
            "text": f"{row['task']} — Category: {row['category']}, Difficulty: {row['difficulty']}",
            "metadata": {
                "type": "task",
                "category": row["category"],
                "difficulty": row["difficulty"],
                "duration": row["duration_estimate"]
            }
        })

    # Frameworks
    for _, row in frameworks.iterrows():
        for doc, vec in zip(docs, vectors):
        collection.add(
            ids=[doc["id"]],
            documents=[doc["text"]],
            metadatas=[doc["metadata"]],
            embeddings=[vec]
        )

    return "Ingestion completed."


# -----------------------------
# FLOW
# -----------------------------

@flow(name="productivity-advisor-ingestion")
def ingestion_flow():
    tasks, frameworks, mappings = load_csv_files()
    docs = build_documents(tasks, frameworks, mappings)
    vectors = embed_documents(docs)
    result = store_in_chroma(docs, vectors)
    return result


if __name__ == "__main__":
    ingestion_flow()