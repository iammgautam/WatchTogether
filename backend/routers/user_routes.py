from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.get("/search", response_model=List[schemas.UserSearchResponse])
def search_users(q: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Search for active users by username, excluding the current user."""
    if not q or len(q) < 2:
        return []
    
    # Simple 'ilike' search on username, limit to 10
    users = db.query(models.User).filter(
        models.User.username.ilike(f"%{q}%"),
        models.User.is_active == True,
        models.User.id != current_user.id
    ).limit(10).all()
    
    return users
