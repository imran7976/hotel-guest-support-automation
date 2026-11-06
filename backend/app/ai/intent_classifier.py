import re
from typing import Optional, Dict, Any
from app.schemas.ai import AIIntentClassification, ExtractedInformation
from app.core.config import settings
from app.core.logging import logger

BOOKING_REF_REGEX = re.compile(r'\b([A-Z]{2,4}[-_]?[0-9]{4,7})\b', re.IGNORECASE)
ROOM_NUM_REGEX = re.compile(r'\b(?:room|suite)\s*#?\s*([0-9]{3,4})\b', re.IGNORECASE)

INTENT_KEYWORDS = {
    "cancellation": ["cancel", "cancellation", "refund", "money back", "void booking", "terminate reservation"],
    "booking_modification": ["change date", "change the date", "change dates", "modify booking", "modify reservation", "extend stay", "change room", "reschedule", "alter booking", "modify"],
    "check_in_information": ["check in", "check-in", "checkin", "arrival time", "early check in", "early check-in", "early arrival", "when can i check in", "checking in"],
    "check_out_information": ["check out", "check-out", "checkout", "late check out", "late check-out", "departure time", "leaving", "checking out"],
    "wifi_issues": ["wifi", "wi-fi", "internet", "password", "network", "ssid", "cannot connect", "no internet", "slow connection"],
    "maintenance_requests": ["air conditioning", "ac", "a/c", "not working", "broken", "leak", "leaking", "toilet", "shower", "hot water", "light bulb", "tv not working", "remote", "noisy"],
    "general_complaint": ["complaint", "unacceptable", "contacted reception twice", "already contacted", "already called", "rude", "dirty", "unhappy", "terrible", "disappointed", "manager", "supervisor"],
    "hotel_facilities": ["pool", "swimming", "gym", "fitness", "spa", "massage", "restaurant", "dining", "breakfast", "buffet", "shuttle", "airport transfer", "parking", "pet", "smoking"],
    "room_availability": ["available", "availability", "any rooms", "book a room", "vacant", "reserve a room"],
    "payment_inquiry": ["payment", "invoice", "receipt", "charge", "credit card", "deposit", "bill", "billing"],
    "booking_inquiry": ["my booking", "reservation details", "confirm booking", "booking status", "reference"]
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
        if "air conditioning" in text.lower() or "ac" in text.lower():
            info.complaint_target = "air conditioning"
        elif "wifi" in text.lower() or "internet" in text.lower():
            info.complaint_target = "Wi-Fi connection"
        elif "shower" in text.lower() or "water" in text.lower():
            info.complaint_target = "plumbing/shower"

        return info

    @classmethod
    def classify(cls, text: str) -> AIIntentClassification:
        clean_text = text.lower()
        extracted = cls.extract_entities(text)

        # Check for urgent complaints & escalation triggers
        is_repeat_complaint = (
            "already contacted" in clean_text or
            "contacted reception twice" in clean_text or
            "called twice" in clean_text or
            "second time" in clean_text or
            "third time" in clean_text or
            "speak to manager" in clean_text or
            "talk to human" in clean_text
        )

        is_maintenance = any(k in clean_text for k in INTENT_KEYWORDS["maintenance_requests"])
        is_cancellation = any(k in clean_text for k in INTENT_KEYWORDS["cancellation"])
        is_modification = any(k in clean_text for k in INTENT_KEYWORDS["booking_modification"])

        # Complaint prioritization
        if is_repeat_complaint or (is_maintenance and is_repeat_complaint):
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

        # Match against remaining keyword groups
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
            priority = "high" if best_intent in ["maintenance_requests", "general_complaint"] else "normal"
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
