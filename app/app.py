import requests
import streamlit as st


API_URL = "http://localhost:8000"


st.title("🧠 Productivity Advisor")


query = st.text_input(
    "Enter your question:"
)


model = st.selectbox(
    "Choose model:",
    ["gpt-5.4-mini"],
)


if st.button("Submit") and query.strip():

    response = requests.post(
        f"{API_URL}/ask",
        json={
            "question": query,
            "model": model,
        },
    )

    response.raise_for_status()

    result = response.json()

    st.session_state["conversation_id"] = (
        result["conversation_id"]
    )

    st.session_state["answer"] = result["answer"]


if "answer" in st.session_state:

    st.subheader("Answer")

    st.write(
        st.session_state["answer"]
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("👍"):

            response = requests.post(
                f"{API_URL}/feedback",
                json={
                    "conversation_id": (
                        st.session_state[
                            "conversation_id"
                        ]
                    ),
                    "feedback": 1,
                },
            )

            response.raise_for_status()

            st.success(
                "Thanks for your feedback!"
            )

    with col2:

        if st.button("👎"):

            response = requests.post(
                f"{API_URL}/feedback",
                json={
                    "conversation_id": (
                        st.session_state[
                            "conversation_id"
                        ]
                    ),
                    "feedback": -1,
                },
            )

            response.raise_for_status()

            st.success(
                "Thanks for your feedback!"
            )