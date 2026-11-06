from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


class GuestService:
    @staticmethod
    def get_by_id(db: Session, guest_id: int) -> Optional[Guest]:
        return db.query(Guest).filter(Guest.id == guest_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Guest]:
        return db.query(Guest).filter(Guest.email == email.lower().strip()).first()

    @staticmethod
    def get_or_create(db: Session, guest_name: str, email: str, phone: Optional[str] = None) -> Guest:
        cleaned_email = email.lower().strip()
        guest = db.query(Guest).filter(Guest.email == cleaned_email).first()
        if guest:
            return guest

        # Split name into first and last
        name_parts = guest_name.strip().split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        guest = Guest(
            first_name=first_name,
            last_name=last_name,
            email=cleaned_email,
            phone=phone,
            vip_status=False
        )
        db.add(guest)
        db.commit()
        db.refresh(guest)
        return guest

    @staticmethod
    def list_guests(db: Session, skip: int = 0, limit: int = 100) -> List[Guest]:
        return db.query(Guest).order_by(Guest.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, guest_id: int, guest_in: GuestUpdate) -> Optional[Guest]:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            return None
        update_data = guest_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(guest, field, value)
        db.commit()
        db.refresh(guest)
        return guest

