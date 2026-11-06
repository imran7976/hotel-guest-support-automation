from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.booking import (
    BookingResponse,
    BookingCreate,
    ModificationRequest,
    CancellationRequest
)
from app.services.booking_service import BookingService
from app.models.booking import Booking

router = APIRouter()


@router.get("", response_model=List[BookingResponse])
def get_bookings(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return BookingService.list_bookings(db, status=status, skip=skip, limit=limit)


@router.get("/availability")
def check_room_availability(
    check_in: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    room_type: Optional[str] = Query(None, description="Optional room type filter"),
    db: Session = Depends(get_db)
):
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")
    return BookingService.check_availability(db, check_in, check_out, room_type)


@router.get("/{booking_reference}", response_model=BookingResponse)
def get_booking_by_ref(booking_reference: str, db: Session = Depends(get_db)):
    booking = BookingService.get_by_reference(db, booking_reference)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking reference not found")
    return booking


@router.post("/{booking_id}/modification-request")
def submit_modification_request(
    booking_id: int,
    request_data: ModificationRequest,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        result = BookingService.request_modification(
            db=db,
            booking_id=booking_id,
            modification=request_data,
            conversation_id=conversation_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{booking_id}/cancellation-request")
def submit_cancellation_request(
    booking_id: int,
    request_data: CancellationRequest,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        result = BookingService.request_cancellation(
            db=db,
            booking_id=booking_id,
            cancellation=request_data,
            conversation_id=conversation_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

