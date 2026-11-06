from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.workflow_log import WorkflowLog
from app.schemas.ai import ProcessInquiryRequest, ProcessInquiryResponse
from app.services.guest_service import GuestService
from app.services.conversation_service import ConversationService
from app.services.booking_service import BookingService
from app.services.escalation_service import EscalationService
from app.ai.intent_classifier import IntentClassifier
from app.ai.rag_engine import RAGEngine
from app.ai.client import OpenAIClientWrapper
from app.ai.business_rules import BusinessRuleValidator
from app.integrations.n8n_client import N8NClient
from app.core.logging import logger


class AIGuestSupportOrchestrator:
    @classmethod
    def process_inquiry(cls, db: Session, request: ProcessInquiryRequest) -> ProcessInquiryResponse:
        logger.info(f"Processing guest inquiry for {request.guest_name} ({request.email})")

        # 1. Identify or register guest
        guest = GuestService.get_or_create(db, request.guest_name, request.email)

        # 2. Check booking reference if provided or extract from text
        booking = None
        if request.booking_reference:
            booking = BookingService.get_by_reference(db, request.booking_reference)

        # 3. Initialize or retrieve conversation
        booking_id = booking.id if booking else None
        conversation = ConversationService.get_or_create_conversation(
            db=db,
            guest_id=guest.id,
            conversation_id=request.conversation_id,
            booking_id=booking_id,
            channel=request.channel
        )

        # 4. Extract intent & entities
        intent_result = IntentClassifier.classify(request.inquiry_message)

        # If booking ref was extracted from text but wasn't in request parameter
        if not booking and intent_result.extracted_information.booking_reference:
            booking = BookingService.get_by_reference(db, intent_result.extracted_information.booking_reference)
            if booking:
                conversation.booking_id = booking.id
                db.commit()

        # 5. Retrieve grounded knowledge via RAG
        knowledge_entries = RAGEngine.retrieve(
            db=db,
            query=request.inquiry_message,
            category=intent_result.intent
        )
        knowledge_texts = [k.content for k in knowledge_entries]

        # 6. Retrieve conversational history
        history = ConversationService.get_conversation_history(db, conversation.id, limit=6)

        # 7. Generate response using OpenAI (or smart fallback)
        ai_response = OpenAIClientWrapper.generate_response(
            guest_message=request.inquiry_message,
            intent_data=intent_result,
            knowledge_context=knowledge_texts,
            conversation_history=history,
            guest_name=guest.first_name
        )

        # 8. Business Rule and Safety Policy Enforcement
        validated_response, is_escalated, escalation_reason = BusinessRuleValidator.validate_and_enforce(
            response=ai_response,
            user_message=request.inquiry_message,
            retrieved_count=len(knowledge_entries)
        )

        # 9. Store Guest message in Database
        guest_msg = ConversationService.add_message(
            db=db,
            conversation_id=conversation.id,
            sender_type="guest",
            content=request.inquiry_message,
            intent=validated_response.intent,
            confidence=validated_response.confidence,
            priority=validated_response.priority,
            requires_human=validated_response.requires_human,
            metadata_json={
                "extracted": validated_response.extracted_information.model_dump(),
                "channel": request.channel
            }
        )

        # 10. Store AI response message in Database
        ai_msg = ConversationService.add_message(
            db=db,
            conversation_id=conversation.id,
            sender_type="ai",
            content=validated_response.response,
            intent=validated_response.intent,
            confidence=validated_response.confidence,
            priority=validated_response.priority,
            requires_human=validated_response.requires_human
        )

        # 11. Handle Escalation ticket if required
        escalation_id: Optional[int] = None
        if validated_response.requires_human:
            escalation = EscalationService.create_escalation(
                db=db,
                conversation_id=conversation.id,
                guest_id=guest.id,
                inquiry_text=request.inquiry_message,
                category=validated_response.intent,
                escalation_reason=escalation_reason or "Automated escalation trigger.",
                priority=validated_response.priority,
                booking_id=conversation.booking_id
            )
            escalation_id = escalation.id

            # Trigger n8n Complaint/Escalation workflow (Workflow 2)
            N8NClient.trigger_webhook_sync(
                endpoint_path="complaint-escalation",
                payload={
                    "escalation_id": escalation.id,
                    "conversation_id": conversation.id,
                    "guest_name": request.guest_name,
                    "guest_email": request.email,
                    "priority": validated_response.priority,
                    "category": validated_response.intent,
                    "reason": escalation_reason,
                    "inquiry": request.inquiry_message
                }
            )

        # 12. Trigger n8n Guest Inquiry workflow (Workflow 1)
        N8NClient.trigger_webhook_sync(
            endpoint_path="guest-inquiry",
            payload={
                "conversation_id": conversation.id,
                "guest_id": guest.id,
                "intent": validated_response.intent,
                "confidence": validated_response.confidence,
                "requires_human": validated_response.requires_human,
                "response": validated_response.response
            }
        )

        return ProcessInquiryResponse(
            conversation_id=conversation.id,
            guest_id=guest.id,
            intent=validated_response.intent,
            confidence=validated_response.confidence,
            priority=validated_response.priority,
            requires_human=validated_response.requires_human,
            response=validated_response.response,
            escalation_id=escalation_id,
            retrieved_knowledge=[k.title for k in knowledge_entries],
            timestamp=datetime.now(timezone.utc).isoformat()
        )

