# 🚀 Productivity Advisor

A Retrieval-Augmented Generation (RAG) application that provides personalized productivity guidance by combining a curated productivity knowledge base, hybrid search, and a large language model.

Built as a project for the [DataCamp LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp).

---

## 📌 Overview

**Productivity Advisor** is an AI assistant designed to help users become more productive by recommending appropriate productivity frameworks, suggesting tasks, improving planning, and reducing overwhelm.

Instead of relying only on a language model's general knowledge, the application retrieves relevant productivity tasks from a curated dataset and uses the retrieved information as context for the LLM.

The application also stores conversations and user feedback so that interactions can be analyzed and the system can be monitored over time.

---

# 🎯 Problem Statement

Many people struggle with questions such as:

- Where should I start?
- What task should I do next?
- How can I stay focused?
- Which productivity technique fits my situation?
- How can I break a large task into manageable steps?
- How should I plan my day?

Traditional chatbots can provide generic advice that may not follow a consistent productivity methodology.

Productivity Advisor addresses this problem by retrieving relevant productivity tasks and frameworks from a curated dataset before generating recommendations.

The goal is to provide practical, context-aware productivity advice that users can immediately apply.

---

# 🎯 Project Goals

The system helps users:

- Find suitable productivity techniques
- Discover tasks that match available time
- Break large tasks into smaller actionable steps
- Improve focus during work or study
- Reduce decision fatigue
- Organize daily and weekly plans
- Receive explanations for why a specific productivity framework is recommended

---

# 📊 Dataset

The project uses a custom productivity dataset generated with ChatGPT and stored in the `data/` directory.

The dataset contains approximately 250 productivity task records. Each record represents a task paired with an appropriate productivity framework and implementation guidance.

### Dataset Fields

| Column | Description |
|---|---|
| `task` | The task or activity |
| `category` | Task category such as Work, Study, Home, Fitness, Personal, or Creative |
| `difficulty` | Estimated task difficulty |
| `duration_estimate` | Estimated completion time |
| `framework_name` | Recommended productivity framework |
| `reasoning` | Why the framework fits the task |
| `instructions` | Step-by-step guidance |
| `tags` | Keywords describing the task |

### Example

| Task | Category | Framework |
|---|---|---|
| Write a project summary | Work | Time Blocking |
| Organize pantry shelves | Home | Task Decomposition |
| Review study notes | Study | Spaced Repetition |
| Practice breathing meditation | Personal | Habit Stacking |

---

# 🧠 RAG Architecture

The application uses a hybrid Retrieval-Augmented Generation pipeline.

```text
                         User Question
                              │
                              ▼
                     ┌─────────────────┐
                     │    Streamlit    │
                     │       UI        │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │    FastAPI      │
                     │      API        │
                     └────────┬────────┘
                              │
                              ▼
                         ┌─────────┐
                         │  rag()  │
                         └────┬────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ hybrid_search()  │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
          MinSearch Keyword         OpenAI Embeddings
              Search                    │
                 │                       ▼
                 │              Cosine Similarity
                 │                       │
                 └───────────┬───────────┘
                             ▼
                      Combined Ranking
                             │
                             ▼
                       Top Documents
                             │
                             ▼
                      Context Assembly
                             │
                             ▼
                         OpenAI LLM
                             │
                             ▼
                      Generated Answer
                             │
                             ▼
                   Relevance Evaluation
                             │
                             ▼
                    API Response + UUID
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
           Streamlit UI               Database
                                      │
                              ┌───────┴────────┐
                              │                │
                        Conversations       Feedback 

```

--- 
# ⚙️ How It Works

The application follows a Retrieval-Augmented Generation workflow:

1. The user submits a productivity-related question.
2. The API receives the request.
3. The query is passed to the RAG pipeline.
4. Hybrid retrieval searches the productivity knowledge base.
5. Keyword relevance and semantic similarity are combined to rank candidate documents.
6. The highest-ranked productivity tasks are assembled into the context.
7. The retrieved context is provided to the language model.
8. The language model generates a productivity recommendation.
9. The generated answer is evaluated for relevance.
10. The API returns the answer together with metadata such as the model used, response time, token usage, cost, and relevance evaluation.
11. Conversations and user feedback can be stored for later analysis.

---

# ✨ Features

- Retrieval-Augmented Generation (RAG)
- Hybrid keyword and semantic search
- Productivity framework recommendations
- Personalized task suggestions
- Step-by-step task instructions
- Context-aware productivity advice
- Explainable recommendations
- Relevance evaluation
- Token usage tracking
- OpenAI cost tracking
- Response-time monitoring
- Conversation storage
- User feedback collection

---

# 🔎 Hybrid Search

The retrieval layer combines keyword-based search with semantic similarity.

## Keyword Search

The application uses **MinSearch** to retrieve candidate documents based on textual relevance.

Different fields are given different boost values:

| Field | Boost |
|---|---:|
| `task` | 2.5 |
| `reasoning` | 2.2 |
| `instructions` | 1.8 |
| `tags` | 1.4 |
| `category` | 1.1 |
| `difficulty` | 0.9 |

The system first retrieves up to 50 keyword-based candidates.

## Semantic Search

The retrieved candidates are then compared using embeddings generated with:

```text
text-embedding-3-small
```
Cosine similarity is used to calculate semantic similarity between the user query and the retrieved documents.

Final Ranking

The final hybrid score combines keyword and semantic scores:
```text
Hybrid Score = 0.4 × Keyword Score + 0.6 × Semantic Score

```
The highest-ranked documents are then returned to the RAG pipeline.

---

# 🤖 LLM Generation

The application uses an OpenAI language model to generate the final productivity recommendation.

The RAG prompt provides the model with:

* The user's question
* Retrieved productivity tasks
* Categories
* Difficulty
* Duration estimates
* Productivity frameworks
* Instructions
* Reasoning
* Tags

The retrieved context is used as the basis for generating the recommendation.

---

# 📈 Evaluation

The project includes both retrieval evaluation and RAG answer evaluation.

Evaluation data is stored in the [data/](data) directory.

Retrieval Evaluation

The initial MinSearch retrieval approach without field boosting achieved:

Hit Rate: 80%
MRR: 60%

The retrieval dataset is stored in: [ground-truth-retrieval.csv](data/ground-truth-retrieval.csv)

---

## RAG Evaluation

The generated answers are evaluated using an LLM-as-a-Judge approach.

The evaluator classifies generated responses as:

* RELEVANT
* PARTLY_RELEVANT
* NON_RELEVANT

The evaluation dataset is stored in: [rag-eval-4o-mini.csv](data/rag-eval-gpt-4o-mini.csv)
For the GPT-4o-mini evaluation across 200 records: 

156 (78%) RELEVANT
36 (18%) PARTLY_RELEVANT
8 (4%) NON_RELEVANT

GPT-4o was also tested and produced similar results to the GPT-5.4-mini configuration.

---

# 📊 Monitoring

The RAG pipeline tracks several metrics for each request:

* Response time
* Prompt tokens
* Completion tokens
* Total tokens
* Evaluation prompt tokens
* Evaluation completion tokens
* Evaluation total tokens
* OpenAI cost
* Relevance classification
* Relevance explanation

This information can be used to monitor system performance, model usage, and operating costs.

---

# 🗄️ Database

The db/ directory contains the database components:
```bash 
db/
├── db.py
└── db_prep.py
```

The database layer is used to support persistence of application data such as conversations and user feedback.

---
### Main Components

#### `productivity_advisor/`

Core application logic.

- **`ingest.py`** — Loads the productivity dataset and builds the MinSearch index.
- **`search.py`** — Implements keyword search and hybrid keyword/semantic retrieval.
- **`rag.py`** — Orchestrates retrieval, context construction, LLM generation, evaluation, token tracking, and cost calculation.
- **`openai_client.py`** — Provides the shared OpenAI client used across the application.

#### `app/`

Contains the Streamlit frontend.

- **`app.py`** — User-facing Productivity Advisor interface.

#### `api.py`

Provides the API layer connecting the frontend with the RAG application.

#### `db/`

Database preparation and persistence logic.

#### `data/`

Contains the productivity dataset and evaluation datasets.

#### `Dockerfile`

Defines the application container.

#### `compose.yaml`

Defines the containerized application environment.

#### `Makefile`

Provides convenient commands for project development and execution.

---

# 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **FastAPI**
- **OpenAI API**
- **MinSearch**
- **NumPy**
- **scikit-learn**
- **Cosine Similarity**
- **PostgreSQL**
- **Docker**
- **Docker Compose**
- **uv**

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/thepassant/productivity-advisor.git
cd productivity-advisor
```
## 2. Install dependencies

This project uses uv for dependency management.
```bash
uv sync
```
## 3. Configure environment variables

Create a .env file and configure the required environment variables, including your OpenAI API key and database configuration.

For example:
```text
OPENAI_API_KEY=your_api_key
```
 ---

# 🚀 Running the Project
## Local Development

Start the API:

```bash
uv run uvicorn api:app --host 0.0.0.0 --port 8000
```

Then start the Streamlit application:

```bash
uv run streamlit run app/app.py
```

The Streamlit application communicates with the API, which runs the RAG pipeline.


## Running with Docker

The repository includes:

```bash
Dockerfile
compose.yaml
```

The application can therefore be run as a containerized service.

Build and start the containers with:

```bash
docker compose up --build
```

```text 
User
 │
 ▼
Streamlit
 │
 ▼
FastAPI
 │
 ▼
RAG Pipeline
 │
 ├── MinSearch
 │     │
 │     └── Keyword Candidates
 │
 ├── OpenAI Embeddings
 │     │
 │     └── Semantic Scores
 │
 └── Hybrid Ranking
        │
        ▼
   Top Documents
        │
        ▼
   Context Assembly
        │
        ▼
   OpenAI LLM
        │
        ▼
 Generated Answer
        │
        ▼
 LLM Relevance Evaluation
        │
        ▼
 API Response
        │
        ├── Answer
        ├── Model
        ├── Response Time
        ├── Token Usage
        ├── Cost
        └── Relevance

```
# 💡 Example Questions

Users can interact with Productivity Advisor using natural language.

Examples:

- "I only have 20 minutes. What should I work on?"
- "How can I improve my focus?"
- "Suggest some quick productivity tasks."
- "I'm feeling overwhelmed. Where should I start?"
- "Help me plan today's work."
- "Which productivity framework should I use for writing?"
- "How can I organize my study session?"
- "Give me tasks that fit into a 30-minute break."
- "How do I break a large project into smaller steps?"

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 🙏 Acknowledgements

Built as the final project for the **DataCamp LLM Zoomcamp**.

Special thanks to the Zoomcamp instructors and the open-source community for providing the learning resources and inspiration for this project.
