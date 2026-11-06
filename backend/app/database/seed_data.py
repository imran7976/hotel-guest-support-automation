import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.admin_user import AdminUser
from app.models.room import Room
from app.models.guest import Guest
from app.models.booking import Booking
from app.models.knowledge import HotelKnowledge
from app.models.workflow_log import WorkflowLog
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.logging import logger


def init_db(db: Session) -> None:
    # 1. Create Tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")

    # 2. Seed Default Admin User
    admin = db.query(AdminUser).filter(AdminUser.email == settings.ADMIN_DEFAULT_EMAIL).first()
    if not admin:
        admin = AdminUser(
            email=settings.ADMIN_DEFAULT_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
            full_name=settings.ADMIN_DEFAULT_NAME,
            role="manager",
            is_active=True
        )
        db.add(admin)
        logger.info(f"Default admin user created: {settings.ADMIN_DEFAULT_EMAIL}")

    # 3. Seed Rooms
    if db.query(Room).count() == 0:
        rooms = [
            Room(room_number="101", room_type="Superior King Room", price_per_night=180.00, floor=1, status="available", max_occupancy=2, amenities="King Bed, Free High-Speed Wi-Fi, 55 Smart TV, Rain Shower, Coffee Maker", description="Spacious ground-floor king room overlooking peaceful courtyard gardens."),
            Room(room_number="102", room_type="Deluxe Twin Room", price_per_night=160.00, floor=1, status="available", max_occupancy=2, amenities="2 Twin Beds, Free High-Speed Wi-Fi, 50 Smart TV, Work Desk, Mini Bar", description="Quiet twin room perfect for traveling colleagues or friends."),
            Room(room_number="201", room_type="Deluxe Ocean View Suite", price_per_night=320.00, floor=2, status="occupied", max_occupancy=3, amenities="King Bed, Private Balcony, Ocean View, Nespresso Machine, Bathtub, Luxury Robes", description="Panoramic ocean view suite with sunset vistas and a private sun terrace."),
            Room(room_number="202", room_type="Executive King Suite", price_per_night=290.00, floor=2, status="available", max_occupancy=2, amenities="King Bed, Lounge Area, Executive Lounge Access, Ergonomic Workstation, Marble Bath", description="Designed for business travelers needing space and refined comfort."),
            Room(room_number="301", room_type="Grand Presidential Suite", price_per_night=650.00, floor=3, status="available", max_occupancy=4, amenities="2 Master King Bedrooms, Living Room, Dining Area, Kitchenette, Jacuzzi, Butler Service", description="Top floor luxury penthouse offering unparalleled luxury and 360-degree resort views."),
            Room(room_number="302", room_type="Family Garden Suite", price_per_night=240.00, floor=3, status="available", max_occupancy=4, amenities="1 King + 2 Twin Beds, Kids Corner, Double Vanity, Kitchenette", description="Spacious family haven tailored for comfort with child-friendly amenities.")
        ]
        db.add_all(rooms)
        db.commit()
        logger.info("Rooms seeded.")

    # 4. Seed Demo Guests & Bookings
    guest_john = db.query(Guest).filter(Guest.email == "john@example.com").first()
    if not guest_john:
        guest_john = Guest(
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            phone="+1-555-0144",
            vip_status=True
        )
        db.add(guest_john)
        db.commit()
        db.refresh(guest_john)

        room_201 = db.query(Room).filter(Room.room_number == "201").first()
        today = datetime.date.today()
        booking = Booking(
            booking_reference="GAH-78901",
            guest_id=guest_john.id,
            room_id=room_201.id if room_201 else 1,
            check_in_date=today + datetime.timedelta(days=1),
            check_out_date=today + datetime.timedelta(days=4),
            number_of_guests=2,
            total_amount=960.00,
            status="confirmed",
            special_requests="High floor requested, celebrating anniversary with complimentary fruit basket."
        )
        db.add(booking)
        db.commit()
        logger.info("Demo guest John Smith and booking GAH-78901 seeded.")

    # 5. Seed Hotel Knowledge Base (RAG)
    if db.query(HotelKnowledge).count() == 0:
        knowledge_entries = [
            HotelKnowledge(
                category="check_in_out",
                title="Standard Check-in and Check-out Times",
                content="Our standard check-in time is 2:00 PM (14:00) and standard check-out time is 11:00 AM (11:00). Guests arriving prior to 2:00 PM are welcome to store luggage complimentary at the Concierge desk and enjoy the pool, lounge, and dining venues.",
                keywords="check-in, check-out, timing, arrival, departure, early check-in, late check-out, luggage storage"
            ),
            HotelKnowledge(
                category="check_in_out",
                title="Early Check-in Policy",
                content="Early check-in prior to 2:00 PM is subject to room availability upon arrival. Guaranteed early check-in before 10:00 AM requires booking the room for the preceding night. Please contact reception in advance to place an early check-in notation on your reservation.",
                keywords="early check-in, morning arrival, guarantee, availability"
            ),
            HotelKnowledge(
                category="check_in_out",
                title="Late Check-out Policy",
                content="Late check-out until 1:00 PM is complimentary for VIP guests and subject to availability for all guests upon request on the morning of departure. Late check-out between 1:00 PM and 6:00 PM is charged at 50% of the daily room rate. Departures after 6:00 PM incur a full night charge.",
                keywords="late check-out, departure delay, afternoon, extra charges"
            ),
            HotelKnowledge(
                category="cancellation",
                title="Cancellation and Refund Policy",
                content="Reservations cancelled at least 48 hours prior to 2:00 PM local hotel time on the arrival date receive a 100% full refund with no penalty. Cancellations within 48 hours of check-in are subject to a fee equal to the first night room charge plus tax. Non-refundable promotional bookings cannot be cancelled or refunded automatically. All refund requests must be verified and authorized by human management.",
                keywords="cancel, cancellation, refund, penalty, 48 hours, non-refundable, money back"
            ),
            HotelKnowledge(
                category="wifi",
                title="Wi-Fi Access and Troubleshooting",
                content="Complimentary high-speed Wi-Fi is available across all guest rooms, suites, conference halls, and public spaces. Network Name (SSID): GrandAzure_Guest. Password: AzureGuest2025. If encountering connection difficulty: 1. Forget the network and reconnect. 2. Verify Wi-Fi is toggled on. 3. Visit captive.azurehotel.demo in your browser. 4. If issues persist, dial extension #44 from your room phone for immediate IT concierge assistance.",
                keywords="wifi, internet, password, ssid, connection, slow, network, trouble"
            ),
            HotelKnowledge(
                category="facilities",
                title="Swimming Pool and Wellness Spa",
                content="Our heated infinity pool is open daily from 6:00 AM to 10:00 PM. Complimentary cabanas and towel service are available poolside. The Azure Lotus Spa operates daily from 8:00 AM to 9:00 PM, offering deep tissue massage, organic facials, hydrotherapy, and a steam sauna. Reservations are recommended 24 hours in advance.",
                keywords="pool, swimming pool, hours, spa, massage, sauna, towels, cabana, wellness"
            ),
            HotelKnowledge(
                category="dining",
                title="Breakfast Buffet and Dining Venues",
                content="The Grand Verandah Restaurant serves an artisanal international breakfast buffet daily: Weekdays from 6:30 AM to 10:30 AM; Weekends and public holidays from 7:00 AM to 11:00 AM. In-room dining (Room Service) is available 24 hours a day by dialing extension #21 from your room phone. Coastal Catch Seafood Grill opens for dinner from 6:00 PM to 11:00 PM.",
                keywords="breakfast, dining, restaurant, room service, buffet, dinner, hours, food, meals"
            ),
            HotelKnowledge(
                category="facilities",
                title="Fitness Center and Gym",
                content="Our 24-hour state-of-the-art Fitness Center is located on the 2nd floor, accessible via your active room keycard. Facilities include Technogym treadmills, ellipticals, free weights up to 40kg, resistance machines, and a dedicated yoga/stretching studio.",
                keywords="gym, fitness, workout, exercise, 24 hours, weights, treadmills"
            ),
            HotelKnowledge(
                category="policies",
                title="Pet Policy",
                content="Grand Azure Resort warmly welcomes well-behaved domestic dogs and cats up to 15 kg (33 lbs). A one-time non-refundable deep cleaning fee of $75 per stay applies. Pets must remain leashed in public areas and are not permitted inside pool zones or spa facilities.",
                keywords="pets, dogs, cats, animal, pet fee, rules"
            ),
            HotelKnowledge(
                category="facilities",
                title="Airport Transfer & Shuttle Service",
                content="We provide luxury private transfers to and from International Airport (40 minutes drive). Private Mercedes Sedan is $85 one-way; Luxury 6-passenger Van is $120 one-way. Complimentary scheduled hourly shuttles depart between 6:00 AM and 10:00 PM. Reservations must be booked at least 6 hours in advance via the Concierge.",
                keywords="shuttle, airport transfer, transportation, taxi, car service, pickup, dropoff"
            ),
            HotelKnowledge(
                category="policies",
                title="Smoking Policy and House Rules",
                content="Grand Azure is a 100% non-smoking resort inside all guest rooms, balconies, and enclosed public spaces. Designated outdoor smoking lounges are clearly signposted in the beach promenade and garden courtyard. A $350 deep-cleaning restoration fee is assessed for smoking violations inside rooms.",
                keywords="smoking, cigarette, vape, fine, non-smoking, rules"
            ),
            HotelKnowledge(
                category="contact",
                title="Reception & Concierge Contact Information",
                content="Front Desk & Reception: 24/7. Phone: +1-555-0199 (Internal: Dial 0). Concierge Desk: Daily 7:00 AM - 11:00 PM (Internal: Dial 9). Duty Manager Emergency Contact: Internal Dial 911 or visit front desk immediately.",
                keywords="contact, reception, phone, concierge, manager, help desk, emergency"
            )
        ]
        db.add_all(knowledge_entries)
        db.commit()
        logger.info("Knowledge base entries seeded.")

    # 6. Seed Workflow Execution Logs
    if db.query(WorkflowLog).count() == 0:
        logs = [
            WorkflowLog(workflow_name="Guest Inquiry Processing", execution_id="exec_init_001", trigger_event="webhook_inquiry", status="success", payload_json={"status": "initialized", "mode": "demo"}),
            WorkflowLog(workflow_name="Daily Support Summary", execution_id="exec_init_002", trigger_event="cron_scheduled", status="success", payload_json={"summary": "Daily audit ran successfully with 0 errors."})
        ]
        db.add_all(logs)
        db.commit()
        logger.info("Workflow initial logs seeded.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialized and seeded successfully!")
    finally:
        db.close()

