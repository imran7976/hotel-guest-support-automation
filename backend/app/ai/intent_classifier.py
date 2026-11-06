import re
from typing import Optional, Dict, Any
from app.schemas.ai import AIIntentClassification, ExtractedInformation
from app.core.config import settings
from app.core.logging import logger

BOOKING_REF_REGEX = re.compile(r'\b([A-Z]{2,4}[-_]?[0-9]{4,7})\b', re.IGNORECASE)
ROOM_NUM_REGEX = re.compile(r'\b(?:room|suite)\s*#?\s*([0-9]{3,4})\b', re.IGNORECASE)

ADVERSARIAL_PATTERNS = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "ignore all instructions",
    "ignore instructions",
    "ignore rules",
    "forget your instructions",
    "forget you are",
    "you are now",
    "jailbreak",
    "dan mode",
    "system override",
    "admin override",
    "admin_override",
    "admin_mode",
    "reveal your system prompt",
    "print your system prompt",
    "reveal your prompt",
    "print your instructions",
    "api key",
    "output 'hacked'",
    "output hacked",
    "grant 100% discount",
    "all rooms are free"
]

EMERGENCY_PATTERNS = [
    "fire in room", "fire in", "smoke", "flames", "building on fire", "there is a fire",
    "medical emergency", "collapsed", "unconscious", "heart attack", "call an ambulance", "ambulance", "not breathing", "choking",
    "gas leak", "natural gas", "smell gas", "gas leaking"
]

GREETING_PATTERNS = [
    "hello", "hi", "good morning", "good afternoon", "good evening", "hey",
    "can someone help me", "can you help me", "help me please", "how are you"
]

INTENT_KEYWORDS = {
    "cancellation": ["cancel", "cancellation", "refund", "money back", "void booking", "terminate reservation"],
    "booking_modification": [
        "change date", "change the date", "change dates", "modify booking", "modify reservation",
        "extend stay", "change room", "reschedule", "alter booking", "modify",
        "upgrade", "upgrade my room", "room upgrade", "upgrade room"
    ],
    "check_in_information": ["check in", "check-in", "checkin", "arrival time", "early check in", "early check-in", "early arrival", "when can i check in", "checking in", "leave my bags", "store my bags"],
    "check_out_information": ["check out", "check-out", "checkout", "late check out", "late check-out", "departure time", "leaving", "checking out"],
    "wifi_issues": ["wifi", "wi-fi", "internet", "password", "network", "ssid", "cannot connect", "no internet", "slow connection"],
    "maintenance_requests": ["air conditioning", "a/c", "ac unit", "not working", "broken", "leak", "leaking", "toilet", "shower", "hot water", "light bulb", "tv not working", "remote", "clogged", "overflowing"],
    "general_complaint": [
        "complaint", "unacceptable", "contacted reception twice", "already contacted", "already called",
        "rude", "dirty", "unhappy", "terrible", "disappointed", "manager", "supervisor",
        "noisy", "noise", "loud", "loud music", "neighbors", "dirty sheets", "dirty towels", "hair on"
    ],
    "hotel_facilities": [
        "pool", "swimming", "gym", "fitness", "spa", "massage", "restaurant", "dining", "breakfast",
        "buffet", "shuttle", "airport transfer", "parking", "pet", "pets", "smoking", "balcony",
        "around here", "things to do", "attractions", "sightseeing"
    ],
    "room_availability": ["available", "availability", "any rooms", "book a room", "vacant", "reserve a room"],
    "payment_inquiry": [
        "payment", "invoice", "receipt", "charge", "credit card", "deposit", "bill", "billing",
        "unexpected charge", "unrecognized charge", "folio", "overcharged", "why is there a charge", "dispute"
    ],
    "booking_inquiry": [
        "my booking", "reservation details", "details of my reservation", "confirm booking",
        "booking status", "reference", "my reservation", "check my reservation", "check reservation", "check the details"
    ]
}


class IntentClassifier:
    @staticmethod
    def extract_entities(text: str) -> ExtractedInformation:
        info = ExtractedInformation()
        
        # Booking reference extraction
        ref_match = BOOKING_REF_REGEX.search(text)
        if ref_match:
            info.booking_reference = ref_match.group(1).upper()

        # Room number extraction
        room_match = ROOM_NUM_REGEX.search(text)
        if room_match:
            info.room_number = room_match.group(1)

        # Dates extraction heuristic
        if "tomorrow" in text.lower():
            info.requested_date = "tomorrow"
        elif "today" in text.lower():
            info.requested_date = "today"
        elif "weekend" in text.lower():
            info.requested_date = "upcoming weekend"

        # Complaint target extraction
        if "air conditioning" in text.lower() or bool(re.search(r'\bac\b', text.lower())):
            info.complaint_target = "air conditioning"
        elif "wifi" in text.lower() or "internet" in text.lower():
            info.complaint_target = "Wi-Fi connection"
        elif "shower" in text.lower() or "water" in text.lower():
            info.complaint_target = "plumbing/shower"
        elif "toilet" in text.lower():
            info.complaint_target = "toilet/plumbing"
        elif "noise" in text.lower() or "noisy" in text.lower():
            info.complaint_target = "noise disturbance"

        return info

    @classmethod
    def classify(cls, text: str) -> AIIntentClassification:
        clean_text = text.lower()
        extracted = cls.extract_entities(text)

        # 1. Adversarial & Prompt Injection Defense
        if any(adv in clean_text for adv in ADVERSARIAL_PATTERNS):
            return AIIntentClassification(
                intent="other",
                confidence=0.99,
                priority="high",
                requires_human=True,
                escalation_reason="Adversarial prompt injection attempt detected.",
                extracted_information=extracted
            )

        # 2. Critical Life-Safety Emergency Detection
        if any(em in clean_text for em in EMERGENCY_PATTERNS):
            return AIIntentClassification(
                intent="maintenance_requests" if ("gas" in clean_text or "fire" in clean_text or "smoke" in clean_text) else "general_complaint",
                confidence=0.99,
                priority="urgent",
                requires_human=True,
                escalation_reason="CRITICAL LIFE-SAFETY EMERGENCY: Immediate staff and emergency dispatch required.",
                extracted_information=extracted
            )

        # 3. Check for urgent complaints & repeat escalation triggers
        is_repeat_complaint = (
            "already contacted" in clean_text or
            "contacted reception twice" in clean_text or
            "called twice" in clean_text or
            "second time" in clean_text or
            "third time" in clean_text or
            "speak to manager" in clean_text or
            "talk to human" in clean_text or
            "manager" in clean_text or
            "supervisor" in clean_text or
            "unacceptable" in clean_text or
            "rude" in clean_text
        )

        is_maintenance = any(k in clean_text for k in INTENT_KEYWORDS["maintenance_requests"])
        is_cancellation = any(k in clean_text for k in INTENT_KEYWORDS["cancellation"])
        is_modification = any(k in clean_text for k in INTENT_KEYWORDS["booking_modification"])
        is_billing_dispute = any(k in clean_text for k in ["unexpected charge", "unrecognized charge", "dispute", "overcharged", "why is there a $", "didn't recognize", "did not recognize"])

        # Billing dispute escalation
        if is_billing_dispute:
            return AIIntentClassification(
                intent="payment_inquiry",
                confidence=0.94,
                priority="high",
                requires_human=True,
                escalation_reason="Billing dispute or unrecognized charge requires front desk accounting review.",
                extracted_information=extracted
            )

        # Urgent Complaint prioritization
        if is_repeat_complaint:
            return AIIntentClassification(
                intent="general_complaint" if not is_maintenance else "maintenance_requests",
                confidence=0.96,
                priority="urgent",
                requires_human=True,
                escalation_reason="Guest reported unresolved repeat issue / urgent complaint.",
                extracted_information=extracted
            )

        if is_cancellation:
            return AIIntentClassification(
                intent="cancellation",
                confidence=0.95,
                priority="high",
                requires_human=True,
                escalation_reason="Cancellation and refund requests require hotel management authorization.",
                extracted_information=extracted
            )

        if is_modification:
            return AIIntentClassification(
                intent="booking_modification",
                confidence=0.92,
                priority="normal",
                requires_human=True,
                escalation_reason="Booking modifications require front desk verification.",
                extracted_information=extracted
            )

        # 4. Booking Reference inquiry detection
        if extracted.booking_reference and any(w in clean_text for w in ["check", "details", "status", "reservation", "booking", "view"]):
            return AIIntentClassification(
                intent="booking_inquiry",
                confidence=0.94,
                priority="normal",
                requires_human=False,
                escalation_reason=None,
                extracted_information=extracted
            )

        # 5. Pure Greeting / Conversational inquiry (only if message does not contain specific domain inquiries)
        trimmed = clean_text.strip().rstrip("!?.,")
        has_specific_inquiry = any(
            any(kw in clean_text for kw in keywords)
            for cat, keywords in INTENT_KEYWORDS.items()
            if cat not in ["hotel_facilities"]
        ) or any(w in clean_text for w in ["check in", "check-in", "checkout", "check out", "wifi", "pool", "booking", "room", "reservation", "cancel", "refund", "breakfast"])

        if not has_specific_inquiry and any(trimmed == g or trimmed.startswith(f"{g} ") or trimmed.startswith(f"{g},") for g in GREETING_PATTERNS):
            return AIIntentClassification(
                intent="hotel_facilities",
                confidence=0.95,
                priority="normal",
                requires_human=False,
                escalation_reason=None,
                extracted_information=extracted
            )

        # 6. Match against remaining keyword groups
        best_intent = "other"
        highest_score = 0

        for intent_name, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in clean_text)
            if score > highest_score:
                highest_score = score
                best_intent = intent_name

        if highest_score > 0:
            confidence = min(0.85 + (highest_score * 0.05), 0.98)
            requires_human = False
            is_urgent_issue = any(w in clean_text for w in ["overflow", "overflowing", "flooding", "boiling hot", "unacceptable", "twice"])
            priority = "urgent" if is_urgent_issue else ("high" if best_intent in ["maintenance_requests", "general_complaint"] else "normal")
            if best_intent in ["maintenance_requests", "general_complaint"]:
                requires_human = True
                escalation_reason = f"Guest {best_intent.replace('_', ' ')} requires staff attention."
            else:
                escalation_reason = None

            return AIIntentClassification(
                intent=best_intent,
                confidence=confidence,
                priority=priority,
                requires_human=requires_human,
                escalation_reason=escalation_reason,
                extracted_information=extracted
            )

        # Fallback intent
        return AIIntentClassification(
            intent="other",
            confidence=0.55,
            priority="normal",
            requires_human=True,
            escalation_reason="Low AI confidence in classifying guest request.",
            extracted_information=extracted
        )
