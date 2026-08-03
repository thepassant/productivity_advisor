import streamlit as st
from rag import rag

# -----------------------------------
# Streamlit Page Config
# -----------------------------------
st.set_page_config(
    page_title="Productivity Advisor",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Productivity Advisor")
st.write("Ask a productivity question and get an answer grounded in your task database.")


# -----------------------------------
# User Input
# -----------------------------------
query = st.text_input("Enter your question:")

model = st.selectbox(
    "Choose model:",
    ["gpt-4o-mini"],
    index=0
)


# -----------------------------------
# Run RAG Pipeline
# -----------------------------------
if st.button("Submit") and query.strip():
    with st.spinner("Thinking..."):
        result = rag(query, model=model)

    # -----------------------------------
    # Display Answer
    # -----------------------------------
    st.subheader("Answer")
    st.write(result["answer"])

    # -----------------------------------
    # Display Relevance Evaluation
    # -----------------------------------
    st.subheader("Relevance Evaluation")
    st.write(f"Relevance: {result['relevance']}")
    st.write(f"Explanation: {result['relevance_explanation']}")

    # -----------------------------------
    # Display Token Usage
    # -----------------------------------
    st.subheader("Token Usage")
    st.write(f"Prompt tokens: {result['prompt_tokens']}")
    st.write(f"Completion tokens: {result['completion_tokens']}")
    st.write(f"Total tokens: {result['total_tokens']}")

    st.write("---")
    st.write(f"Eval prompt tokens: {result['eval_prompt_tokens']}")
    st.write(f"Eval completion tokens: {result['eval_completion_tokens']}")
    st.write(f"Eval total tokens: {result['eval_total_tokens']}")

    # -----------------------------------
    # Display Cost
    # -----------------------------------
    st.subheader("Estimated Cost")
    st.write(f"${result['openai_cost']:.6f}")
