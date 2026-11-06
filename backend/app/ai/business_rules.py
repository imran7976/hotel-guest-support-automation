from typing import Tuple, Optional
from app.schemas.ai import AIGeneratedResponse
from app.core.config import settings
from app.core.logging import logger


class BusinessRuleValidator:
    @staticmethod
    def validate_and_enforce(
        response: AIGeneratedResponse,
        user_message: str,
        retrieved_count: int
    ) -> Tuple[AIGeneratedResponse, bool, Optional[str]]:
        """
        Validates AI response against hotel business rules and compliance policies.
        Returns: (AIGeneratedResponse, is_escalated, escalation_reason)
        """
        lower_msg = user_message.lower()
        needs_escalation = response.requires_human
        escalation_reason = response.escalation_reason

        # 1. AI Confidence Threshold check
        if response.confidence < settings.AI_CONFIDENCE_THRESHOLD:
            needs_escalation = True
            escalation_reason = f"AI confidence ({response.confidence:.2f}) below threshold ({settings.AI_CONFIDENCE_THRESHOLD})."
            logger.info(f"Escalation triggered: {escalation_reason}")

        # 2. Financial & Cancellation Guardrail
        # AI must NEVER promise a refund or confirm cancellation without staff approval
        if response.intent == "cancellation" or "refund" in lower_msg or "cancel" in lower_msg:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = "Cancellations and refunds require front-desk management authorization."
            # Sanitize response if AI erroneously promised an immediate refund
            if "i have refunded" in response.response.lower() or "refund has been processed" in response.response.lower():
                response.response = (
                    "Per Grand Azure Resort policy, all cancellation and refund requests must be verified "
                    "and authorized by hotel management. Your request has been forwarded to our front desk team "
                    "for priority review."
                )

        # 3. Booking Modification Guardrail
        if response.intent == "booking_modification" or "change date" in lower_msg:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = "Booking modifications require front-desk reservation review."

        # 4. Emergency / Urgent Maintenance & Repeated Complaints
        urgent_signals = ["air conditioning", "ac", "broken", "leak", "twice", "contacted reception", "emergency", "manager"]
        if any(sig in lower_msg for sig in urgent_signals) and ("not working" in lower_msg or "twice" in lower_msg or "manager" in lower_msg):
            needs_escalation = True
            response.priority = "urgent"
            if not escalation_reason:
                escalation_reason = "Urgent guest maintenance complaint requiring immediate engineering dispatch."

        # 5. Missing Knowledge Base Guardrail
        if retrieved_count == 0 and response.intent not in ["booking_inquiry", "booking_modification", "cancellation"]:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = "No grounded knowledge base articles found to verify hotel policy."

        # Apply flags to final response
        response.requires_human = needs_escalation
        response.escalation_reason = escalation_reason

        return response, needs_escalation, escalation_reason

