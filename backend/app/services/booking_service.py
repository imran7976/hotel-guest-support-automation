from datetime import date, datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.models.room import Room
from app.models.guest import Guest
from app.models.escalation import Escalation
from app.schemas.booking import ModificationRequest, CancellationRequest


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

        escalation = Escalation(
            conversation_id=conversation_id or f"conv_mod_{booking.booking_reference}",
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

        escalation = Escalation(
            conversation_id=conversation_id or f"conv_canc_{booking.booking_reference}",
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

