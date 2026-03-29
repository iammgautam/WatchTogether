from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/api/rooms",
    tags=["Rooms"]
)

@router.post("/", response_model=schemas.RoomResponse)
def create_room(room_data: schemas.RoomCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Create a new room and assign initial participant invitations. Limit 10."""
    if len(room_data.invited_user_ids) > 10:
        raise HTTPException(status_code=400, detail="Cannot invite more than 10 users.")
    
    # Create the base Room
    new_room = models.Room(
        name=room_data.name,
        admin_id=current_user.id
    )
    db.add(new_room)
    db.flush() # ensure new_room gets its ID generated immediately
    
    # Ensure creator is implicitly a room member
    admin_member = models.RoomMember(
        room_id=new_room.id,
        user_id=current_user.id
    )
    db.add(admin_member)
    
    # Fetch valid invited users
    if room_data.invited_user_ids:
        valid_users = db.query(models.User).filter(models.User.id.in_(room_data.invited_user_ids)).all()
        for u in valid_users:
            if u.id != current_user.id:
                member_assoc = models.RoomMember(
                    room_id=new_room.id,
                    user_id=u.id
                )
                db.add(member_assoc)
            
    db.commit()
    db.refresh(new_room)
    
    return new_room

@router.get("/me")
def get_my_rooms(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve rooms administered by the user and rooms user is invited to."""
    
    my_rooms = db.query(models.Room).filter(models.Room.admin_id == current_user.id).all()
    
    # Subquery to get distinct room IDs the user is a member of
    member_room_ids_subq = db.query(models.RoomMember.room_id).filter(
        models.RoomMember.user_id == current_user.id
    ).subquery()
    
    # Rooms user belongs to but did not create
    invitations = db.query(models.Room).filter(
        models.Room.id.in_(member_room_ids_subq),
        models.Room.admin_id != current_user.id
    ).all()
    
    # We will let FastAPI implicitly JSON-serialize these SQLAlchemy proxy lists
    return {
        "my_rooms": my_rooms,
        "invitations": invitations
    }

@router.get("/{room_id}/messages", response_model=List[schemas.MessageResponse])
def get_room_messages(room_id: str, limit: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Fetch the last N messages for a specific room."""
    # Check if user is a member of the room
    membership = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this room")
    
    messages = db.query(models.Message).filter(
        models.Message.room_id == room_id
    ).order_by(models.Message.created_at.desc()).limit(limit).all()
    
    # Return in chronological order (oldest first) for the chat UI
    return messages[::-1]
