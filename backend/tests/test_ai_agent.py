import pytest
from app.ai.intent_classifier import IntentClassifier
from app.ai.business_rules import BusinessRuleValidator
from app.ai.rag_engine import RAGEngine
from app.schemas.ai import AIGeneratedResponse, ExtractedInformation, ProcessInquiryRequest
from app.ai.response_generator import AIGuestSupportOrchestrator


def test_intent_classification_categories():
    test_cases = [
        ("What time can I check in tomorrow?", "check_in_information", False),
        ("What is the checkout time?", "check_out_information", False),
        ("What is the wifi password for guest rooms?", "wifi_issues", False),
        ("Do you have a swimming pool and gym?", "hotel_facilities", False),
        ("Are there any rooms available next weekend?", "room_availability", False),
        ("Please change the date of my reservation GAH-78901", "booking_modification", True),
        ("I need to cancel my booking and get a refund", "cancellation", True),
        ("The toilet is leaking and AC is not working", "maintenance_requests", True),
        ("The staff at reception was extremely rude and unhelpful!", "general_complaint", True),
        ("Where can I find the invoice for my payment?", "payment_inquiry", False),
        ("Can you check the status of my booking?", "booking_inquiry", False),
        ("Tell me a random story about mars", "other", True),
    ]

    for inquiry, expected_intent, expected_human in test_cases:
        result = IntentClassifier.classify(inquiry)
        assert result.intent == expected_intent, f"Failed for inquiry: {inquiry}. Expected {expected_intent}, got {result.intent}"
        assert result.requires_human == expected_human, f"Human requirement mismatch for: {inquiry}"


def test_business_rules_safeguards():
    # 1. Auto-refund safeguard
    fake_response = AIGeneratedResponse(
        intent="cancellation",
        confidence=0.98,
        priority="normal",
        requires_human=False,
        response="I have refunded your booking of $500 immediately.",
        extracted_information=ExtractedInformation(booking_reference="GAH-78901")
    )
    validated, is_escalated, reason = BusinessRuleValidator.validate_and_enforce(
        response=fake_response,
        user_message="Please cancel my reservation and refund my payment",
        retrieved_count=2
    )
    assert is_escalated is True
    assert validated.requires_human is True
    assert "management" in validated.response.lower()

    # 2. Low confidence cutoff
    low_conf_response = AIGeneratedResponse(
        intent="other",
        confidence=0.45,
        priority="normal",
        requires_human=False,
        response="I am not sure what you mean.",
        extracted_information=ExtractedInformation()
    )
    validated_low, is_esc_low, reason_low = BusinessRuleValidator.validate_and_enforce(
        response=low_conf_response,
        user_message="quantum fluctuations in the lobby",
        retrieved_count=0
    )
    assert is_esc_low is True
    assert "below threshold" in reason_low.lower()


def test_end_to_end_ai_orchestration(db_session):
    # Scenario 1: Check-in inquiry
    req1 = ProcessInquiryRequest(
        guest_name="John Smith",
        email="john@example.com",
        inquiry_message="Hello, I have a booking for tomorrow. Could you tell me the check-in time and whether I can request an early check-in?",
        booking_reference="GAH-78901"
    )
    res1 = AIGuestSupportOrchestrator.process_inquiry(db_session, req1)
    assert res1.intent == "check_in_information"
    assert res1.requires_human is False
    assert "2:00 PM" in res1.response
    assert len(res1.retrieved_knowledge) > 0

    # Scenario 2: Urgent AC maintenance complaint
    req2 = ProcessInquiryRequest(
        guest_name="John Smith",
        email="john@example.com",
        inquiry_message="My room's air conditioning is not working, and I have already contacted reception twice."
    )
    res2 = AIGuestSupportOrchestrator.process_inquiry(db_session, req2)
    assert res2.priority in ["urgent", "high"]
    assert res2.requires_human is True
    assert res2.escalation_id is not None

    # Scenario 3: Cancellation request
    req3 = ProcessInquiryRequest(
        guest_name="John Smith",
        email="john@example.com",
        inquiry_message="Please cancel my reservation and issue a refund.",
        booking_reference="GAH-78901"
    )
    res3 = AIGuestSupportOrchestrator.process_inquiry(db_session, req3)
    assert res3.intent == "cancellation"
    assert res3.requires_human is True
    assert res3.escalation_id is not None
