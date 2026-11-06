from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.ai import (
    ProcessInquiryRequest,
    ProcessInquiryResponse,
    AIGeneratedResponse
)
from app.ai.response_generator import AIGuestSupportOrchestrator

router = APIRouter()


@router.post("/process-inquiry", response_model=ProcessInquiryResponse, status_code=status.HTTP_200_OK)
def process_guest_inquiry(
    request: ProcessInquiryRequest,
    db: Session = Depends(get_db)
):
    """
    Core AI Support Endpoint:
    1. Identifies/creates guest & conversation
    2. Classifies intent & extracts booking/date info
    3. Retrieves grounded RAG context from hotel knowledge
    4. Generates AI response using OpenAI (or smart fallback)
    5. Validates against hotel business safeguards
    6. Triggers escalation and n8n webhooks if needed
    7. Stores audit trail in MySQL
    """
    return AIGuestSupportOrchestrator.process_inquiry(db=db, request=request)


@router.post("/generate-response", response_model=AIGeneratedResponse)
def generate_direct_response(
    inquiry_message: str,
    guest_name: str = "Guest",
    conversation_history_limit: int = 4,
    db: Session = Depends(get_db)
):
    from app.ai.intent_classifier import IntentClassifier
    from app.ai.rag_engine import RAGEngine
    from app.ai.client import OpenAIClientWrapper

    intent_result = IntentClassifier.classify(inquiry_message)
    knowledge_entries = RAGEngine.retrieve(db, inquiry_message, category=intent_result.intent)
    
    response = OpenAIClientWrapper.generate_response(
        guest_message=inquiry_message,
        intent_data=intent_result,
        knowledge_context=[k.content for k in knowledge_entries],
        conversation_history=[],
        guest_name=guest_name
    )
    return response

