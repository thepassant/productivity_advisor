import json
from time import time

import dotenv
from openai import OpenAI

from productivity_advisor.search import hybrid_search

dotenv.load_dotenv()
client = OpenAI()


# -----------------------------
# MODELS
# -----------------------------

DEFAULT_MODEL = "gpt-4.5-mini"
EVAL_MODEL = "gpt-4o"


# -----------------------------
# MODEL PRICING
# Price per 1M tokens
# -----------------------------

MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60,
    },
}


# -----------------------------
# PROMPT TEMPLATES
# -----------------------------

prompt_template = """
You're a productivity advisor. Answer the QUESTION based on the CONTEXT from our productivity tasks database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()


entry_template = """
task: {task}
category: {category}
difficulty: {difficulty}
duration_estimate: {duration_estimate}
instructions: {instructions}
reasoning: {reasoning}
tags: {tags}
""".strip()


# -----------------------------
# BUILD PROMPT
# -----------------------------

def build_prompt(query, search_results):
    context = ""

    for doc in search_results:
        context += entry_template.format(**doc) + "\n\n"

    return prompt_template.format(
        question=query,
        context=context
    ).strip()


# -----------------------------
# LLM CALL
# -----------------------------

def llm(prompt, model=DEFAULT_MODEL):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


# -----------------------------
# EVALUATION PROMPT
# -----------------------------

evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.

Based on the relevance of the generated answer, classify it as:
"NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Provide your evaluation in parsable JSON:

{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Brief explanation]"
}
""".strip()


# -----------------------------
# RELEVANCE EVALUATION
# -----------------------------

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(
        question=question,
        answer=answer
    )

    evaluation, tokens = llm(
        prompt,
        model=EVAL_MODEL
    )

    try:
        json_eval = json.loads(evaluation)

        valid_relevance = {
            "NON_RELEVANT",
            "PARTLY_RELEVANT",
            "RELEVANT",
        }

        if json_eval.get("Relevance") not in valid_relevance:
            return {
                "Relevance": "UNKNOWN",
                "Explanation": "Invalid relevance value"
            }, tokens

        return json_eval, tokens

    except json.JSONDecodeError:
        return {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation"
        }, tokens


# -----------------------------
# COST CALCULATION
# -----------------------------

def calculate_openai_cost(model, tokens):
    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return 0.0

    input_cost = (
        tokens["prompt_tokens"] / 1_000_000
    ) * pricing["input"]

    output_cost = (
        tokens["completion_tokens"] / 1_000_000
    ) * pricing["output"]

    return input_cost + output_cost


# -----------------------------
# FULL RAG PIPELINE
# -----------------------------

def rag(query, model=DEFAULT_MODEL):
    start_time = time()

    # Retrieve relevant documents
    search_results = hybrid_search(query)

    # Build RAG prompt
    prompt = build_prompt(
        query,
        search_results
    )

    # Generate answer
    answer, token_stats = llm(
        prompt,
        model=model
    )

    # Evaluate answer
    relevance, rel_token_stats = evaluate_relevance(
        query,
        answer
    )

    # Response time
    response_time = time() - start_time

    # Calculate costs
    openai_cost_rag = calculate_openai_cost(
        model,
        token_stats
    )

    openai_cost_eval = calculate_openai_cost(
        EVAL_MODEL,
        rel_token_stats
    )

    openai_cost = (
        openai_cost_rag +
        openai_cost_eval
    )

    return {
        "answer": answer,
        "model_used": model,
        "response_time": response_time,

        "relevance": relevance.get(
            "Relevance",
            "UNKNOWN"
        ),

        "relevance_explanation": relevance.get(
            "Explanation",
            "Failed to parse evaluation"
        ),

        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],

        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],

        "openai_cost": openai_cost,
    }