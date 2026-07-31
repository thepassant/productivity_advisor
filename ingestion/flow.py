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
