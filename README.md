# 🚀 Productivity Advisor

**Productivity Advisor** is a Retrieval-Augmented Generation (RAG) application built as the **final project for LLM Zoomcamp**.

The application helps users organize work, prioritize tasks, and discover suitable productivity frameworks by combining semantic search with Large Language Models. It demonstrates a complete end-to-end RAG workflow including automated ingestion, hybrid retrieval, query rewriting, document re-ranking, evaluation, monitoring, and containerized deployment.

---

## ✨ Features

- 📚 Rich productivity knowledge base
- ⚙️ Automated ingestion pipeline with Prefect
- 🔎 Hybrid retrieval (Vector + Keyword Search)
- ✍️ LLM-powered query rewriting
- 🎯 LLM-based document re-ranking
- 🤖 Context-aware productivity recommendations
- 📈 Monitoring dashboard and user feedback
- 🐳 Fully containerized with Docker Compose
- 🧪 Retrieval and LLM evaluation

---

# 🏗️ System Architecture

```
                ┌────────────────────┐
                │   CSV Dataset      │
                └─────────┬──────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Prefect Ingestion    │
              │ • Load data           │
              │ • Chunk Documents     │
              │ • Generate Embeddings │
              └─────────┬─────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │   SQLite Vector DB   │
              └─────────┬────────────┘
                        │
                        ▼
                 User Question
                        │
                        ▼
             ┌────────────────────────┐
             │ Query Rewriting (LLM)  │
             └─────────┬──────────────┘
                       ▼
          ┌────────────────────────────┐
          │ Hybrid Retrieval           │
          │ • Semantic Search          │
          │ • Metadata Filtering       │
          └─────────┬──────────────────┘
                    ▼
         ┌─────────────────────────────┐
         │ LLM Document Re-ranking     │
         └─────────┬───────────────────┘
                   ▼
          ┌────────────────────────────┐
          │ Context Assembly           │
          └─────────┬──────────────────┘
                    ▼
           ┌──────────────────────────┐
           │ LLM Response Generation  │
           └─────────┬────────────────┘
                     ▼
              Streamlit Interface
```

---

# 📂 Project Structure

```
productivity-advisor/
│
├── app/
│   ├── ui.py
│   ├── monitoring.py
│   └── feedback.py
│
├── config/
│   ├── prompts.py
│   └── settings.py
│
├── data/
│   ├── raw_data.csv
│   ├── tasks.csv
│   └── cleaned_data.csv
│
├── evaluation/
│   ├── retrieval_eval.py
│   ├── llm_eval.py
│   └── benchmark.py
│
├── ingestion/
│   └── ingest.py
│
├── rag/
│   ├── rag.py
│   ├── search.py
│   └── pipeline.py
│
├── vectorstore/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── README.md
├── requirements.txt
└── .env.example
```

---

# 🧠 Knowledge Base

The assistant uses four structured datasets:

| Dataset | Description |
|----------|-------------|
| **productivity_frameworks.csv** | Productivity methods and frameworks |
| **tasks.csv** | Example work, study, home and personal tasks |
| **goals.csv** | Short, medium and long-term goals |
| **framework_task_mapping.csv** | Relationships between tasks and recommended frameworks |

During ingestion these datasets are:

- Loaded
- Chunked
- Embedded
- Stored inside ChromaDB

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/<username>/productivity-advisor.git
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Copy the environment file

```bash
cp .env.example .env
```

Add your API keys to `.env`.

---

# 🚀 Running the Project

## 1. Run Ingestion

```bash
python ingestion/ui.py
```

This will:

- Load CSV datasets
- Generate embeddings
- Build the Chroma vector database

---

## 2. Launch the Application

```bash
streamlit run app/ui.py
```

---

## 3. Run with Docker

```bash
docker-compose up --build
```

---

# 🔍 Retrieval Pipeline

The retrieval process consists of:

1. User submits a question
2. LLM rewrites the query
3. Hybrid retrieval searches ChromaDB
4. Retrieved documents are re-ranked
5. Relevant context is assembled
6. LLM generates the final recommendation

---

# 📊 Evaluation

The project evaluates multiple retrieval strategies.

### Retrieval Evaluation

- Semantic Search
- Keyword Search
- Hybrid Search
- LLM Re-ranking

### LLM Evaluation

- Prompt comparison
- Response quality
- LLM-as-a-Judge scoring

The best-performing configuration is used in the final application.

---

# 📈 Monitoring

The monitoring dashboard tracks:

- 👍 Positive feedback
- 👎 Negative feedback
- Query volume
- Retrieval latency
- Most recommended frameworks
- User satisfaction trends

---

# 🛠️ Tech Stack

- Python
- Streamlit
- Prefect
- ChromaDB
- OpenAI API
- Sentence Transformers
- Docker
- SQLite / PostgreSQL

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 🙏 Acknowledgements

Built as the final project for **LLM Zoomcamp**.

Special thanks to the Zoomcamp instructors and the open-source community for providing the learning resources that inspired this project.
