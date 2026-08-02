import json
from time import time
from openai import OpenAI
from ingestion.ingest import ingest 

client = OpenAI()
index = ingest.load_index()


# -----------------------------
# SEARCH
# -----------------------------
def search(query):
    boost = {
        "task": 2.15,
        "instructions": 1.8,
        "reasoning": 2.2,
        "tags": 1.4,
        "category": 1.1,
        "difficulty": 0.9
    }

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results


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

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


# -----------------------------
# LLM CALL
# -----------------------------
def llm(prompt, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
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
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="gpt-4o-mini")

    try:
        json_eval = json.loads(evaluation)
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
    if model == "gpt-4o-mini":
        return (
            tokens["prompt_tokens"] * 0.00015 +
            tokens["completion_tokens"] * 0.0006
        ) / 1000

    return 0.0


# -----------------------------
# FULL RAG PIPELINE
# -----------------------------
def rag(query, model="gpt-4o-mini"):
    t0 = time()

    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt, model=model)

    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)
    openai_cost = openai_cost_rag + openai_cost_eval

    return {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get("Explanation", "Failed to parse evaluation"),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }
