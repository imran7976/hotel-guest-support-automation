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
            f"EXTRACTED ENTITIES: {intent_data.extracted_information.model_dump()}\n\n"
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
        lower_msg = guest_message.lower()

        # Adversarial Prompt Injection Defense
        if escalation_reason == "Adversarial prompt injection attempt detected." or any(w in lower_msg for w in ["ignore all previous", "jailbreak", "system override", "output 'hacked'", "you are now a pirate", "reveal your system prompt", "admin_override", "admin override"]):
            response_text = (
                f"{greeting} I am the AI Front Desk Concierge for Grand Azure Resort & Hotel. "
                "I can only assist with verified hotel bookings, guest services, amenities, and inquiries. "
                "Per hotel policy, any cancellations, refunds, or financial modifications strictly require front desk management approval. "
                "How may I assist you with your stay today?"
            )
            requires_human = True
            priority = "high"
            escalation_reason = "Adversarial prompt injection attempt detected."

        # Critical Life-Safety Emergency Protocol
        elif any(em in lower_msg for em in ["fire in", "smoke", "flames", "medical emergency", "collapsed", "unconscious", "ambulance", "heart attack", "gas leak", "natural gas", "smell gas"]):
            response_text = (
                "CRITICAL EMERGENCY ALERT: If there is an active fire or life-threatening medical emergency, please evacuate the area immediately. "
                "Our front desk and emergency response personnel are being notified right now. "
                "You can also dial 911 or internal extension 0 from any room phone for immediate direct dispatch."
            )
            requires_human = True
            priority = "urgent"
            escalation_reason = "CRITICAL LIFE-SAFETY EMERGENCY: Immediate staff and emergency dispatch required."

        # Pure Greetings & Conversational Inquiries (only when no specific intent like check-in was identified)
        elif intent in ["other", "hotel_facilities"] and not any(w in lower_msg for w in ["check in", "check-in", "checkout", "check out", "wifi", "pool", "booking", "room", "reservation", "cancel", "refund", "breakfast"]) and any(lower_msg.strip().rstrip("!.,?").startswith(g) or lower_msg.strip().rstrip("!.,?") == g for g in ["hello", "hi", "good morning", "good afternoon", "good evening", "hey", "can someone help me", "can you help me"]):
            response_text = (
                f"{greeting} Welcome to Grand Azure Resort & Hotel! I am your AI Front Desk Concierge. "
                "How may I assist you today with your stay, reservation, or hotel amenities?"
            )
            requires_human = False
            priority = "normal"
            escalation_reason = None

        elif intent == "check_in_information":
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
                "To ensure proper room inventory and rate adjustments, all date, room, and upgrade changes require "
                "front-desk verification and management approval. A member of our reservations team will review your request shortly."
            )
            requires_human = True
            escalation_reason = "Booking modification request requires front desk approval."
        elif intent == "booking_inquiry":
            if extracted.booking_reference:
                response_text = (
                    f"{greeting} Your reservation details for booking reference {extracted.booking_reference} "
                    "are confirmed in our system. You are booked with Grand Azure Resort."
                )
            else:
                response_text = (
                    f"{greeting} To look up your reservation, please provide your booking reference number (e.g. GAH-78901) "
                    "or the email address used when booking."
                )
            requires_human = False
            escalation_reason = None
        elif intent == "payment_inquiry":
            if any(w in lower_msg for w in ["unexpected", "unrecognized", "why is there", "dispute", "didn't recognize", "did not recognize"]):
                response_text = (
                    f"{greeting} We have logged your billing inquiry regarding the unrecognized charge on your folio. "
                    "Our front desk accounting team will review your statement and contact you directly with an itemized explanation."
                )
                requires_human = True
                priority = "high"
                escalation_reason = "Billing dispute requires front desk accounting review."
            else:
                response_text = (
                    f"{greeting} We accept all major credit cards (Visa, MasterCard, American Express) as well as debit cards and cash deposits at check-in. "
                    "An itemized invoice is provided upon departure."
                )
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

