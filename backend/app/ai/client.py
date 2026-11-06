import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.schemas.ai import AIGeneratedResponse, AIIntentClassification, ExtractedInformation
from app.ai.prompts import HOTEL_SUPPORT_SYSTEM_PROMPT
from app.core.config import settings
from app.core.logging import logger


class OpenAIClientWrapper:
    @classmethod
    def get_client(cls) -> Optional[OpenAI]:
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() and not settings.OPENAI_API_KEY.startswith("your-"):
            try:
                return OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
        return None

    @classmethod
    def generate_response(
        cls,
        guest_message: str,
        intent_data: AIIntentClassification,
        knowledge_context: List[str],
        conversation_history: List[Dict[str, str]],
        guest_name: str = "Guest"
    ) -> AIGeneratedResponse:
        client = cls.get_client()

        # Build prompt payload
        system_content = HOTEL_SUPPORT_SYSTEM_PROMPT
        grounded_context = "\n\n".join(knowledge_context) if knowledge_context else "No specific policy retrieved."
        user_prompt = (
            f"GUEST NAME: {guest_name}\n"
            f"IDENTIFIED INTENT: {intent_data.intent}\n"
            f"EXTRACTED ENTITIES: {intent_data.extracted_information.dict()}\n\n"
            f"VERIFIED HOTEL KNOWLEDGE CONTEXT:\n{grounded_context}\n\n"
            f"GUEST INQUIRY:\n{guest_message}"
        )

        if client:
            try:
                messages = [{"role": "system", "content": system_content}]
                # Add past turns
                for turn in conversation_history[-4:]:
                    messages.append(turn)
                messages.append({"role": "user", "content": user_prompt})

                logger.info(f"Calling OpenAI API using model: {settings.OPENAI_MODEL_NAME}")
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL_NAME,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=settings.AI_TEMPERATURE,
                    max_tokens=600
                )
                raw_json = completion.choices[0].message.content
                parsed = json.loads(raw_json)
                
                # Strict Pydantic validation
                return AIGeneratedResponse(**parsed)
            except Exception as e:
                logger.error(f"OpenAI API call failed or returned invalid format: {e}. Falling back to internal engine.", exc_info=True)

        # Intelligent grounded fallback generation (Safe Demo / Offline mode)
        return cls._generate_grounded_fallback(guest_message, intent_data, knowledge_context, guest_name)

    @classmethod
    def _generate_grounded_fallback(
        cls,
        guest_message: str,
        intent_data: AIIntentClassification,
        knowledge_context: List[str],
        guest_name: str
    ) -> AIGeneratedResponse:
        """
        Deterministic, grounded fallback generator ensuring tests and demos
        work smoothly and reliably without incurring external API failures.
        """
        intent = intent_data.intent
        extracted = intent_data.extracted_information
        requires_human = intent_data.requires_human
        priority = intent_data.priority
        escalation_reason = intent_data.escalation_reason

        # Default greeting
        greeting = f"Hello {guest_name}, thank you for contacting Grand Azure Resort."

        if intent == "check_in_information":
            response_text = (
                f"{greeting} Our standard check-in time is 2:00 PM (14:00) and check-out is 11:00 AM. "
                "Early check-in prior to 2:00 PM is subject to room availability upon arrival. "
                "If you arrive early, our concierge will be delighted to store your luggage complimentary while you enjoy our facilities."
            )
        elif intent == "check_out_information":
            response_text = (
                f"{greeting} Standard check-out time is 11:00 AM. "
                "Late check-out until 1:00 PM is complimentary for VIP guests, subject to availability. "
                "Late departures between 1:00 PM and 6:00 PM incur a 50% room rate fee."
            )
        elif intent == "wifi_issues":
            response_text = (
                f"{greeting} Complimentary high-speed Wi-Fi is available across the resort. "
                "Network Name: GrandAzure_Guest | Password: AzureGuest2025. "
                "If you experience connection difficulties, please try forgetting the network and reconnecting, or dial extension #44 from your room."
            )
        elif intent == "cancellation":
            response_text = (
                f"{greeting} Per our hotel policy, reservations cancelled at least 48 hours prior to check-in "
                "receive a 100% full refund. However, all cancellation and refund requests must be verified "
                "and approved by our front desk management team. We have logged your request for management review."
            )
            requires_human = True
            priority = "high"
            escalation_reason = "Cancellation and refund request escalated for front desk management approval."
        elif intent == "booking_modification":
            response_text = (
                f"{greeting} We have received your booking modification request. "
                "To ensure proper room inventory and rate adjustments, all date and room changes require "
                "front-desk verification. A member of our reservations team will review your request shortly."
            )
            requires_human = True
            escalation_reason = "Booking modification request requires front desk approval."
        elif intent in ["maintenance_requests", "general_complaint"]:
            response_text = (
                f"{greeting} We sincerely apologize for the inconvenience you are experiencing"
                + (f" with your {extracted.complaint_target}" if extracted.complaint_target else "")
                + ". We have escalated this issue as high priority to our front desk duty manager and maintenance engineering team for immediate inspection."
            )
            requires_human = True
            priority = "urgent" if intent_data.priority == "urgent" else "high"
            escalation_reason = "Guest complaint / maintenance issue escalated for urgent staff resolution."
        elif intent == "hotel_facilities":
            if knowledge_context:
                response_text = f"{greeting} {knowledge_context[0]}"
            else:
                response_text = f"{greeting} Our resort offers an infinity swimming pool (6:00 AM - 10:00 PM), 24-hour fitness center, luxury Lotus Spa, and multiple dining venues."
        else:
            if knowledge_context:
                response_text = f"{greeting} {knowledge_context[0]}"
            else:
                response_text = (
                    f"{greeting} Thank you for your inquiry. To ensure you receive accurate and up-to-date information, "
                    "I have forwarded your question to our front-desk reception team who will assist you shortly."
                )
                requires_human = True
                escalation_reason = "General inquiry requiring front desk verification."

        return AIGeneratedResponse(
            intent=intent,
            confidence=intent_data.confidence,
            priority=priority,
            requires_human=requires_human,
            escalation_reason=escalation_reason,
            response=response_text,
            extracted_information=extracted
        )

