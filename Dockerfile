FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uv run python db/db_prep.py && uv run uvicorn api:app --host 0.0.0.0 --port 8000 & uv run streamlit run app/app.py --server.address=0.0.0.0 --server.port=8501"]