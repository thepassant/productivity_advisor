from typing import Literal
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from db.db import save_conversation, save_feedback
from productivity_advisor.rag import rag


app = FastAPI()


class AskRequest(BaseModel):
    question: str
    model: str = "gpt-4o-mini"


class FeedbackRequest(BaseModel):
    conversation_id: str
    feedback: Literal[1, -1]


@app.post("/ask")
def ask(request: AskRequest):
    conversation_id = str(uuid4())

    result = rag(
        request.question,
        model=request.model,
    )

    save_conversation(
        conversation_id=conversation_id,
        question=request.question,
        result=result,
    )

    return {
        "conversation_id": conversation_id,
        **result,
    }


@app.post("/feedback")
def feedback(request: FeedbackRequest):

    save_feedback(
        conversation_id=request.conversation_id,
        feedback=request.feedback,
    )

    return {
        "status": "received",
        "conversation_id": request.conversation_id,
        "feedback": request.feedback,
    }