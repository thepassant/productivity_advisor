import os

import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        dbname=os.getenv(
            "POSTGRES_DB",
            "productivity_advisor",
        ),
    )


# ---------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------

def init_db():
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id UUID PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                model TEXT NOT NULL,
                response_time FLOAT,
                relevance TEXT,
                relevance_explanation TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                eval_prompt_tokens INTEGER,
                eval_completion_tokens INTEGER,
                eval_total_tokens INTEGER,
                openai_cost FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                conversation_id UUID NOT NULL,
                feedback INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT fk_conversation
                    FOREIGN KEY (conversation_id)
                    REFERENCES conversations(conversation_id),

                CONSTRAINT valid_feedback
                    CHECK (feedback IN (-1, 1))
            );
            """
        )

        conn.commit()

        cur.close()

    finally:
        conn.close()


# ---------------------------------------------------------
# SAVE CONVERSATION
# ---------------------------------------------------------

def save_conversation(
    conversation_id,
    question,
    result,
):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO conversations (
                conversation_id,
                question,
                answer,
                model,
                response_time,
                relevance,
                relevance_explanation,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                eval_prompt_tokens,
                eval_completion_tokens,
                eval_total_tokens,
                openai_cost
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            );
            """,
            (
                conversation_id,
                question,
                result["answer"],
                result["model_used"],
                result["response_time"],
                result["relevance"],
                result["relevance_explanation"],
                result["prompt_tokens"],
                result["completion_tokens"],
                result["total_tokens"],
                result["eval_prompt_tokens"],
                result["eval_completion_tokens"],
                result["eval_total_tokens"],
                result["openai_cost"],
            ),
        )

        conn.commit()

        cur.close()

    finally:
        conn.close()


# ---------------------------------------------------------
# SAVE FEEDBACK
# ---------------------------------------------------------

def save_feedback(
    conversation_id,
    feedback,
):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO feedback (
                conversation_id,
                feedback
            )
            VALUES (%s, %s);
            """,
            (
                conversation_id,
                feedback,
            ),
        )

        conn.commit()

        cur.close()

    finally:
        conn.close()


# ---------------------------------------------------------
# GET CONVERSATION
# ---------------------------------------------------------

def get_conversation(conversation_id):
    conn = get_connection()

    try:
        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute(
            """
            SELECT *
            FROM conversations
            WHERE conversation_id = %s;
            """,
            (conversation_id,),
        )

        conversation = cur.fetchone()

        cur.close()

        return conversation

    finally:
        conn.close()