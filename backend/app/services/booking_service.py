import secrets
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.models.room import Room
from app.models.guest import Guest
from app.models.escalation import Escalation
from app.schemas.booking import ModificationRequest, CancellationRequest, BookingCreateRequest
from app.services.guest_service import GuestService
from app.services.conversation_service import ConversationService



class BookingService:
    @staticmethod
    def get_by_reference(db: Session, reference: str) -> Optional[Booking]:
        return (
            db.query(Booking)
            .filter(Booking.booking_reference == reference.strip().upper())
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def list_bookings(
        db: Session,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Booking]:
        query = db.query(Booking)
        if status and status != "all":
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.check_in_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def check_availability(
        db: Session,
        check_in_date: date,
        check_out_date: date,
        room_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Simulated room availability check against bookings overlapping dates."""
        query = db.query(Room).filter(Room.status != "maintenance")
        if room_type:
            query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
        
        all_rooms = query.all()
        available_rooms = []

        for room in all_rooms:
            overlapping_booking = (
                db.query(Booking)
                .filter(
                    Booking.room_id == room.id,
                    Booking.status.in_(["confirmed", "pending_modification"]),
                    Booking.check_in_date < check_out_date,
                    Booking.check_out_date > check_in_date
                )
                .first()
            )
            if not overlapping_booking:
                available_rooms.append({
                    "room_id": room.id,
                    "room_number": room.room_number,
                    "room_type": room.room_type,
                    "price_per_night": float(room.price_per_night),
                    "max_occupancy": room.max_occupancy,
                    "amenities": room.amenities,
                    "floor": room.floor,
                    "is_available": True
                })

        return available_rooms

    @staticmethod
    def create_booking(db: Session, booking_data: BookingCreateRequest) -> Booking:
        """Creates a new confirmed demo booking with guest auto-resolution and room assignment."""
        if booking_data.check_out_date <= booking_data.check_in_date:
            raise ValueError("Check-out date must be strictly after check-in date.")

        # 1. Resolve or create guest
        guest = GuestService.get_or_create(
            db=db,
            guest_name=booking_data.guest_name,
            email=booking_data.guest_email
        )

        # 2. Find eligible available room
        query = db.query(Room).filter(Room.status != "maintenance")
        if booking_data.room_number:
            query = query.filter(Room.room_number == booking_data.room_number.strip())
        elif booking_data.room_type:
            query = query.filter(Room.room_type.ilike(f"%{booking_data.room_type.strip()}%"))

        candidate_rooms = query.all()
        selected_room = None
        for room in candidate_rooms:
            overlap = (
                db.query(Booking)
                .filter(
                    Booking.room_id == room.id,
                    Booking.status.in_(["confirmed", "pending_modification"]),
                    Booking.check_in_date < booking_data.check_out_date,
                    Booking.check_out_date > booking_data.check_in_date
                )
                .first()
            )
            if not overlap:
                selected_room = room
                break

        if not selected_room:
            raise ValueError("No available room found matching criteria for the requested dates.")

        # 3. Compute cost
        nights = max(1, (booking_data.check_out_date - booking_data.check_in_date).days)
        total_amount = Decimal(str(nights)) * Decimal(str(selected_room.price_per_night))

        # 4. Generate reference
        for _ in range(10):
            ref = f"GAH-{secrets.token_hex(3).upper()}"
            if not db.query(Booking).filter(Booking.booking_reference == ref).first():
                break
        else:
            ref = f"GAH-{uuid.uuid4().hex[:6].upper()}"

        booking = Booking(
            booking_reference=ref,
            guest_id=guest.id,
            room_id=selected_room.id,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            total_amount=total_amount,
            status="confirmed",
            special_requests=booking_data.special_requests
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def request_modification(
        db: Session,
        booking_id: int,
        modification: ModificationRequest,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking ID {booking_id} not found.")

        # Set status to pending_modification
        booking.status = "pending_modification"
        
        # Human approval required: create escalation
        inquiry_text = (
            f"Booking Modification Request for Ref {booking.booking_reference}: "
            f"Dates: {modification.new_check_in_date or booking.check_in_date} to {modification.new_check_out_date or booking.check_out_date}. "
            f"Room Type: {modification.new_room_type or booking.room.room_type}. "
            f"Reason: {modification.reason}"
        )

        # Ensure conversation exists to satisfy foreign key integrity
        conv = ConversationService.get_or_create_conversation(
            db=db,
            guest_id=booking.guest_id,
            conversation_id=conversation_id,
            booking_id=booking.id,
            channel="web_chat"
        )

        escalation = Escalation(
            conversation_id=conv.id,
            guest_id=booking.guest_id,
            booking_id=booking.id,
            inquiry_text=inquiry_text,
            category="booking_modification",
            priority="normal",
            status="pending",
            escalation_reason="Booking modifications require front-desk staff verification and approval."
        )
        db.add(escalation)
        db.commit()
        db.refresh(booking)
        db.refresh(escalation)

        return {
            "status": "pending_approval",
            "booking_reference": booking.booking_reference,
            "escalation_id": escalation.id,
            "message": "Your booking modification request has been submitted and is awaiting human front-desk approval."
        }

    @staticmethod
    def request_cancellation(
        db: Session,
        booking_id: int,
        cancellation: CancellationRequest,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking ID {booking_id} not found.")

        # Set status to pending_cancellation
        booking.status = "pending_cancellation"

        inquiry_text = (
            f"Cancellation and Refund Request for Ref {booking.booking_reference}. "
            f"Reason: {cancellation.reason}. "
            f"Refund Requested: {cancellation.request_refund}."
        )

        # Ensure conversation exists to satisfy foreign key integrity
        conv = ConversationService.get_or_create_conversation(
            db=db,
            guest_id=booking.guest_id,
            conversation_id=conversation_id,
            booking_id=booking.id,
            channel="web_chat"
        )

        escalation = Escalation(
            conversation_id=conv.id,
            guest_id=booking.guest_id,
            booking_id=booking.id,
            inquiry_text=inquiry_text,
            category="cancellation",
            priority="high",
            status="pending",
            escalation_reason="Cancellations and refunds require front-desk management authorization per hotel policy."
        )
        db.add(escalation)
        db.commit()
        db.refresh(booking)
        db.refresh(escalation)

        return {
            "status": "pending_approval",
            "booking_reference": booking.booking_reference,
            "escalation_id": escalation.id,
            "message": "Your cancellation request has been logged and escalated to hotel management for verification. Automatic refunds are not issued without human authorization."
        }

