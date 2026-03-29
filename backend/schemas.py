from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginUserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: LoginUserInfo | None = None

class TokenData(BaseModel):
    username: str | None = None

class UserSearchResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    name: str
    invited_user_ids: List[int]

class RoomMemberResponse(BaseModel):
    user_id: int
    user: UserSearchResponse

    class Config:
        from_attributes = True

class RoomResponse(BaseModel):
    id: str
    name: str
    admin_id: int
    created_at: datetime
    members: List[RoomMemberResponse]

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    room_id: str
    user_id: int
    content: str
    created_at: datetime
    user: UserSearchResponse

    class Config:
        from_attributes = True
