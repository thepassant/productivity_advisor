from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.db import save_conversation, save_feedback
from productivity_advisor.rag import ( DEFAULT_MODEL, MODEL_PRICING, rag, )


app = FastAPI()


class AskRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL


class FeedbackRequest(BaseModel):
    conversation_id: str
    feedback: Literal[1, -1]


@app.post("/ask")
def ask(request: AskRequest):
    if request.model not in MODEL_PRICING:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported model",
                "model": request.model,
                "supported_models": list(
                    MODEL_PRICING.keys()
                ),
            },
        )

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