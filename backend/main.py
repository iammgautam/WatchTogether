from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

#Import our database configuration and models
from database import engine, get_db
import models
from routers import auth_routes, user_routes, room_routes, websocket_routes

# Database is now managed by Alembic
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# This is critical! It allows our Vue frontend to talk to our API safely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(room_routes.router)
app.include_router(websocket_routes.router)

@app.get("/api/ping")
def get_ping():
    return {"message": "Pong! The FastAPI backend is alive and connected!"}

# --- New Test Route ---
@app.post("/api/test-db")
def test_db_connection(username: str, db: Session = Depends(get_db)):
    """
    This route injects the database session using `Depends(get_db)`.
    It creates a test user to verify the database is connected.
    """
    # Create an instance of our User model
    new_user = models.User(username=username, email=f"{username}@example.com")
    
    # Add to session and commit to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Success! Connected to DB & saved user.", "user_id": new_user.id}