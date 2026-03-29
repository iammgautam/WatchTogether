from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import json
import auth, models
from database import get_db
from room_manager import manager

router = APIRouter()

@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Verify the JWT token from the query parameter
    try:
        user = auth.get_user_from_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check if user is a member of the room
    membership = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == user.id
    ).first()

    if not membership:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect to the manager
    await manager.connect(room_id, user.id, websocket)

    # Broadcast user_joined
    await manager.broadcast_to_room(room_id, {
        "event": "user_joined",
        "user_id": user.id,
        "username": user.username
    })

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            event = message_data.get("event")

            if event == "chat":
                # Persist message to DB
                new_msg = models.Message(
                    room_id=room_id,
                    user_id=user.id,
                    content=message_data.get("content")
                )
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)

                # Broadcast to all
                await manager.broadcast_to_room(room_id, {
                    "event": "chat",
                    "id": new_msg.id,
                    "room_id": room_id,
                    "user_id": user.id,
                    "username": user.username,
                    "content": new_msg.content,
                    "created_at": str(new_msg.created_at)
                })

            elif event in ["webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"]:
                # Signaling: Send to specific target user
                target_user_id = message_data.get("target_user_id")
                if target_user_id:
                    # Forward the message as is, but include sender info
                    message_data["sender_user_id"] = user.id
                    message_data["sender_username"] = user.username
                    await manager.send_to_user(room_id, target_user_id, message_data)

    except WebSocketDisconnect:
        manager.disconnect(room_id, user.id)
        # Broadcast user_left
        await manager.broadcast_to_room(room_id, {
            "event": "user_left",
            "user_id": user.id,
            "username": user.username
        })
    except Exception:
        manager.disconnect(room_id, user.id)
