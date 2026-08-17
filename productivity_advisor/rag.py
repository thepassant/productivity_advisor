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
EVAL_MODEL = "gpt-4.5-mini"


# -----------------------------
# MODEL PRICING
# Price per 1M tokens
# -----------------------------

MODEL_PRICING = {
    "gpt-5.4-mini": {
        "input": 0.75,
        "cached_input": 0.075,
        "output": 4.50,
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


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.

Based on the relevance of the generated answer, classify it as:
"NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Question:
{question}

Generated Answer:
{answer}

Return ONLY valid JSON:

{{
    "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
    "Explanation": "Brief explanation"
}}
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
                "content": prompt,
            }
        ],
    )

    answer = response.choices[0].message.content

    cached_prompt_tokens = 0

    if response.usage.prompt_tokens_details:
        cached_prompt_tokens = (
            response
            .usage
            .prompt_tokens_details
            .cached_tokens
            or 0
        )

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "cached_prompt_tokens": cached_prompt_tokens,
    }

    return answer, token_stats



# -----------------------------
# RELEVANCE EVALUATION
# -----------------------------

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(
        question=question,
        answer=answer,
    )

    evaluation, tokens = llm(
        prompt,
        model=EVAL_MODEL,
    )

    try:
        json_eval = json.loads(evaluation)

    except json.JSONDecodeError:
        return {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation",
        }, tokens

    valid_relevance = {
        "NON_RELEVANT",
        "PARTLY_RELEVANT",
        "RELEVANT",
    }

    relevance = json_eval.get("Relevance")

    if relevance not in valid_relevance:
        return {
            "Relevance": "UNKNOWN",
            "Explanation": "Invalid relevance value",
        }, tokens

    return {
        "Relevance": relevance,
        "Explanation": json_eval.get(
            "Explanation",
            "",
        ),
    }, tokens

# -----------------------------
# COST CALCULATION
# -----------------------------

def calculate_cost(tokens, model):
    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        raise ValueError(
            f"No pricing configured for model: {model}"
        )

    input_tokens = tokens["prompt_tokens"]
    output_tokens = tokens["completion_tokens"]

    cached_tokens = tokens.get(
        "cached_prompt_tokens",
        0,
    )

    if cached_tokens > input_tokens:
        raise ValueError(
            "Cached input tokens cannot exceed input tokens"
        )

    uncached_input_tokens = (
        input_tokens - cached_tokens
    )

    input_cost = (
        uncached_input_tokens / 1_000_000
    ) * pricing["input"]

    cached_input_cost = (
        cached_tokens / 1_000_000
    ) * pricing["cached_input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output"]

    total_cost = (
        input_cost
        + cached_input_cost
        + output_cost
    )

    return {
        "input_cost": input_cost,
        "cached_input_cost": cached_input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }


def calculate_total_cost(usages):
    return sum(
        calculate_cost(
            usage,
            model,
        )["total_cost"]
        for model, usage in usages
    )


# -----------------------------
# FULL RAG PIPELINE
# -----------------------------

def rag(query, model=DEFAULT_MODEL):
    start_time = time()

    # Retrieve relevant documents
    search_start = time()

    search_results = hybrid_search(query)

    search_time = time() - search_start

    # Build RAG prompt
    prompt = build_prompt(
        query,
        search_results
    )

    # Generate answer
    generation_start = time()

    answer, token_stats = llm(
        prompt,
        model=model,
    )

    generation_time = (
        time() - generation_start
    )


    # Evaluate answer
    evaluation_start = time()

    relevance, rel_token_stats = (
        evaluate_relevance(
            query,
            answer,
        )
    )

    evaluation_time = (
        time() - evaluation_start
    )
    #Calculate costs
    generation_cost = calculate_cost(
        token_stats,
        model,
    )

    evaluation_cost = calculate_cost(
        rel_token_stats,
        EVAL_MODEL,
    )

    total_llm_cost = calculate_total_cost([
        (model, token_stats),
        (EVAL_MODEL, rel_token_stats),
    ])

    # Response time
    response_time = time() - start_time

    return {
        "answer": answer,

        "model_used": model,

        "response_time": response_time,

        "search_time": search_time,

        "generation_time": generation_time,

        "evaluation_time": evaluation_time,

        "relevance": relevance.get(
            "Relevance",
            "UNKNOWN",
        ),

        "relevance_explanation": relevance.get(
            "Explanation",
            "Failed to parse evaluation",
        ),

        "prompt_tokens": token_stats[
            "prompt_tokens"
        ],

        "completion_tokens": token_stats[
            "completion_tokens"
        ],

        "total_tokens": token_stats[
            "total_tokens"
        ],

        "cached_prompt_tokens": token_stats[
            "cached_prompt_tokens"
        ],

        "eval_prompt_tokens": rel_token_stats[
            "prompt_tokens"
        ],

        "eval_completion_tokens": rel_token_stats[
            "completion_tokens"
        ],

        "eval_total_tokens": rel_token_stats[
            "total_tokens"
        ],

        "cost": {
            "generation": generation_cost,
            "evaluation": evaluation_cost,
            "total": total_llm_cost,
        },
    }