#!/usr/bin/env python3
"""
Hotel Guest Support Automation - End-to-End Demo Script
Executes the three master test scenarios against the backend services.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.database.session import SessionLocal
from app.database.seed_data import init_db
from app.ai.response_generator import AIGuestSupportOrchestrator
from app.schemas.ai import ProcessInquiryRequest
from app.models.escalation import Escalation


def run_scenario(title: str, inquiry: str, booking_ref: str = None):
    print("\n" + "=" * 80)
    print(f"SCENARIO: {title}")
    print("=" * 80)
    print(f"Guest: John Smith (john@example.com)")
    print(f"Inquiry: \"{inquiry}\"")
    if booking_ref:
        print(f"Booking Reference: {booking_ref}")
    print("-" * 80)

    db = SessionLocal()
    try:
        req = ProcessInquiryRequest(
            guest_name="John Smith",
            email="john@example.com",
            inquiry_message=inquiry,
            booking_reference=booking_ref,
            channel="demo_script"
        )
        res = AIGuestSupportOrchestrator.process_inquiry(db, req)

        print(f"Intent Identified:      {res.intent}")
        print(f"Confidence Score:       {res.confidence * 100:.1f}%")
        print(f"Priority Level:         {res.priority.upper()}")
        print(f"Requires Human Staff:   {res.requires_human}")
        if res.escalation_id:
            esc = db.query(Escalation).filter(Escalation.id == res.escalation_id).first()
            print(f"Escalation Ticket ID:   #{res.escalation_id} (Reason: {esc.escalation_reason if esc else 'N/A'})")
        print(f"RAG Grounded Sources:   {', '.join(res.retrieved_knowledge) if res.retrieved_knowledge else 'None'}")
        print("\nAI Concierge Response:")
        print(f"\"{res.response}\"")
    finally:
        db.close()


def main():
    print("Initializing Database & Seed Data...")
    db = SessionLocal()
    init_db(db)
    db.close()

    # Scenario 1
    run_scenario(
        title="1. Booking & Check-in Inquiry",
        inquiry="Hello, I have a booking for tomorrow. Could you tell me the check-in time and whether I can request an early check-in?",
        booking_ref="GAH-78901"
    )

    # Scenario 2
    run_scenario(
        title="2. Urgent Maintenance Complaint (Air Conditioning)",
        inquiry="My room's air conditioning is not working, and I have already contacted reception twice."
    )

    # Scenario 3
    run_scenario(
        title="3. Reservation Cancellation & Refund Request",
        inquiry="Please cancel my reservation and issue a refund.",
        booking_ref="GAH-78901"
    )

    print("\n" + "=" * 80)
    print("DEMO SCENARIOS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()

