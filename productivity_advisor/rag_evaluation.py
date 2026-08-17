import os

import pandas as pd

from productivity_advisor.rag import rag


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DATA_PATH = os.getenv(
    "RAG_EVAL_DATA_PATH",
    "data/rag-eval-gpt-4o.csv",
)

OUTPUT_PATH = os.getenv(
    "RAG_EVAL_OUTPUT_PATH",
    "data/rag_evaluation_results.csv",
)

MODEL = os.getenv(
    "RAG_EVAL_MODEL",
    "gpt-5.4-mini",
)

RETRIEVAL_METHODS = [
    "keyword",
    "semantic",
    "hybrid",
]

EVAL_LIMIT = int(
    os.getenv("RAG_EVAL_LIMIT", "20")
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_evaluation_data(path=DATA_PATH):
    df = pd.read_csv(path)

    print(f"Loaded {len(df)} evaluation records")

    return df


# ---------------------------------------------------------
# FIND QUESTION COLUMN
# ---------------------------------------------------------

def get_question(row):
    """
    Return the question from the evaluation row.

    Update this function if your CSV uses a different
    column name.
    """

    possible_columns = [
        "question",
        "Question",
        "query",
        "Query",
    ]

    for column in possible_columns:
        if column in row.index:
            return row[column]

    raise ValueError(
        "Could not find a question column in the "
        "evaluation dataset."
    )


# ---------------------------------------------------------
# RUN EVALUATION
# ---------------------------------------------------------

def run_evaluation(
    data_path=DATA_PATH,
    model=MODEL,
):
    df = load_evaluation_data(data_path)

    if EVAL_LIMIT > 0:
        df = df.head(EVAL_LIMIT)

    print(
        f"Running evaluation on {len(df)} records"
    )
    results = []

    total = len(df)

    for i, row in df.iterrows():

        question = get_question(row)

        print(
            f"\nEvaluating {i + 1}/{total}: "
            f"{question}"
        )

        for retrieval_method in RETRIEVAL_METHODS:

            print(
                f"  Retrieval: "
                f"{retrieval_method}"
            )

            try:

                result = rag(
                    question,
                    model=model,
                    retrieval_method=retrieval_method,
                )

                results.append({
                    "question": question,
                    "retrieval_method": (
                        retrieval_method
                    ),
                    "answer": result["answer"],
                    "model_used": result[
                        "model_used"
                    ],
                    "relevance": result[
                        "relevance"
                    ],
                    "relevance_explanation": (
                        result[
                            "relevance_explanation"
                        ]
                    ),
                    "response_time": result[
                        "response_time"
                    ],
                    "search_time": result[
                        "search_time"
                    ],
                    "generation_time": result[
                        "generation_time"
                    ],
                    "evaluation_time": result[
                        "evaluation_time"
                    ],
                    "prompt_tokens": result[
                        "prompt_tokens"
                    ],
                    "completion_tokens": result[
                        "completion_tokens"
                    ],
                    "total_tokens": result[
                        "total_tokens"
                    ],
                    "cached_prompt_tokens": result[
                        "cached_prompt_tokens"
                    ],
                    "eval_prompt_tokens": result[
                        "eval_prompt_tokens"
                    ],
                    "eval_completion_tokens": result[
                        "eval_completion_tokens"
                    ],
                    "eval_total_tokens": result[
                        "eval_total_tokens"
                    ],
                    "generation_cost": result[
                        "cost"
                    ]["generation"]["total_cost"],
                    "evaluation_cost": result[
                        "cost"
                    ]["evaluation"]["total_cost"],
                    "total_cost": result[
                        "cost"
                    ]["total"],
                })

            except Exception as e:

                print(
                    f"    ERROR: {e}"
                )

                results.append({
                    "question": question,
                    "retrieval_method": (
                        retrieval_method
                    ),
                    "answer": None,
                    "model_used": model,
                    "relevance": "ERROR",
                    "relevance_explanation": str(e),
                })

    return pd.DataFrame(results)


# ---------------------------------------------------------
# CALCULATE METRICS
# ---------------------------------------------------------

def calculate_metrics(results):

    metrics = {}

    for method in RETRIEVAL_METHODS:

        method_results = results[
            results["retrieval_method"]
            == method
        ]

        total = len(method_results)

        if total == 0:
            continue

        relevant = (
            method_results["relevance"]
            .eq("RELEVANT")
            .sum()
        )

        partly_relevant = (
            method_results["relevance"]
            .eq("PARTLY_RELEVANT")
            .sum()
        )

        non_relevant = (
            method_results["relevance"]
            .eq("NON_RELEVANT")
            .sum()
        )

        unknown = total - (
            relevant
            + partly_relevant
            + non_relevant
        )

        metrics[method] = {
            "total": total,

            "relevant": relevant,

            "relevant_pct": (
                relevant / total * 100
            ),

            "partly_relevant": (
                partly_relevant
            ),

            "partly_relevant_pct": (
                partly_relevant
                / total
                * 100
            ),

            "non_relevant": (
                non_relevant
            ),

            "non_relevant_pct": (
                non_relevant
                / total
                * 100
            ),

            "unknown": unknown,

            "unknown_pct": (
                unknown
                / total
                * 100
            ),
        }

    return metrics


# ---------------------------------------------------------
# PRINT SUMMARY
# ---------------------------------------------------------

def print_metrics(metrics):

    print()
    print("=" * 70)
    print("PRODUCTIVITY ADVISOR - RETRIEVAL EVALUATION")
    print("=" * 70)

    for method, values in metrics.items():

        print()
        print(f"Retrieval method: {method}")
        print("-" * 40)

        print(
            f"Total: "
            f"{values['total']}"
        )

        print(
            f"RELEVANT: "
            f"{values['relevant']} "
            f"({values['relevant_pct']:.1f}%)"
        )

        print(
            f"PARTLY_RELEVANT: "
            f"{values['partly_relevant']} "
            f"({values['partly_relevant_pct']:.1f}%)"
        )

        print(
            f"NON_RELEVANT: "
            f"{values['non_relevant']} "
            f"({values['non_relevant_pct']:.1f}%)"
        )

        print(
            f"UNKNOWN / ERROR: "
            f"{values['unknown']} "
            f"({values['unknown_pct']:.1f}%)"
        )

    print()
    print("=" * 70)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    results = run_evaluation()

    metrics = calculate_metrics(results)

    print_metrics(metrics)

    results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print(
        f"Detailed results saved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()