from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.services.guest_service import GuestService

router = APIRouter()


@router.post("", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_db)):
    existing = GuestService.get_by_email(db, guest_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Guest with this email already exists")
    guest = GuestService.get_or_create(db, f"{guest_in.first_name} {guest_in.last_name}", guest_in.email, guest_in.phone)
    return guest


@router.get("", response_model=List[GuestResponse])
def get_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return GuestService.list_guests(db, skip=skip, limit=limit)


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest_by_id(guest_id: int, db: Session = Depends(get_db)):
    guest = GuestService.get_by_id(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

